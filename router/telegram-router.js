// Central Telegram Router for Multiple MCP Instances
// Handles bidirectional communication between Telegram and multiple MCP servers

require('dotenv').config();
const express = require('express');
const TelegramBot = require('node-telegram-bot-api');
const axios = require('axios');
const { v4: uuidv4 } = require('uuid');
const multer = require('multer');
const path = require('path');
const fs = require('fs');

// Ensure uploads directory exists
const uploadsDir = path.join(__dirname, 'uploads');
if (!fs.existsSync(uploadsDir)) {
  fs.mkdirSync(uploadsDir, { recursive: true });
}

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, uploadsDir);
  },
  filename: (req, file, cb) => {
    const uniqueName = `${uuidv4()}${path.extname(file.originalname)}`;
    cb(null, uniqueName);
  }
});

const upload = multer({
  storage,
  limits: { fileSize: 10 * 1024 * 1024 }, // 10MB limit
  fileFilter: (req, file, cb) => {
    const allowedTypes = /jpeg|jpg|png|gif|webp/;
    const ext = allowedTypes.test(path.extname(file.originalname).toLowerCase());
    const mime = allowedTypes.test(file.mimetype);
    
    if (ext && mime) {
      cb(null, true);
    } else {
      cb(new Error('Only image files (JPEG, PNG, GIF, WebP) are allowed'));
    }
  }
});

class TelegramRouter {
  constructor(telegramToken, routerPort = 8080) {
    this.bot = new TelegramBot(telegramToken, { polling: true });
    this.app = express();
    this.app.use(express.json({ limit: '50mb' })); // Increased for base64 images
    
    // Enable CORS for all origins
    this.app.use((req, res, next) => {
      res.header('Access-Control-Allow-Origin', '*');
      res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
      res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept');
      if (req.method === 'OPTIONS') {
        return res.sendStatus(200);
      }
      next();
    });
    
    // Serve uploaded images
    this.app.use('/uploads', express.static(uploadsDir));
    
    // Track active sessions: session_id -> instance metadata
    this.sessions = new Map();
    
    // Track instances: instance_id -> connection info
    this.instances = new Map();
    
    // Track message threads: telegram_msg_id -> session_id
    this.messageThreads = new Map();
    
    // Track media groups for multi-image albums
    this.mediaGroups = new Map(); // media_group_id -> {messages: [], timer: ...}
    
    // Configuration
    this.config = {
      sessionCleanupInterval: parseInt(process.env.SESSION_CLEANUP_INTERVAL) || 300000, // 5 min
      sessionMaxAge: parseInt(process.env.SESSION_MAX_AGE) || 1800000, // 30 min
      chatId: process.env.TELEGRAM_CHAT_ID
    };
    
    this.setupRoutes();
    this.setupTelegramHandlers();
    this.startServer(routerPort);
    this.startCleanupTask();
  }

  setupRoutes() {
    // Serve uploaded images
    this.app.use('/uploads', express.static(path.join(__dirname, 'uploads')));

    // Endpoint for MCP instances to register
    this.app.post('/register', (req, res) => {
      const { instance_id, instance_name, port, callback_url } = req.body;
      
      if (!instance_id || !instance_name || !callback_url) {
        return res.status(400).json({ error: 'Missing required fields' });
      }
      
      this.instances.set(instance_id, {
        instance_name,
        port,
        callback_url,
        last_seen: Date.now(),
        registered_at: Date.now()
      });
      
      console.log(`✅ Registered: ${instance_name} (${instance_id}) on port ${port}`);
      console.log(`   Callback URL: ${callback_url}`);
      res.json({ status: 'registered', instance_id });
    });

    // Endpoint for MCP instances to send messages to Telegram
    this.app.post('/send', async (req, res) => {
      const { 
        instance_id, 
        session_id, 
        message, 
        context,
        reply_markup,
        images // New: array of base64 images
      } = req.body;
      
      if (!instance_id || !session_id || !message) {
        return res.status(400).json({ error: 'Missing required fields' });
      }
      
      const instance = this.instances.get(instance_id);
      if (!instance) {
        return res.status(404).json({ error: 'Instance not registered' });
      }

      // Update last seen
      instance.last_seen = Date.now();

      try {
        // Format message with instance identifier
        const messageParts = this.formatOutgoingMessage(
          instance.instance_name,
          message,
          session_id
        );

        // Send each part
        let lastMsgId;
        for (const part of messageParts) {
          const sentMsg = await this.bot.sendMessage(
            this.config.chatId,
            part.text,
            { 
              parse_mode: 'Markdown'
            }
          );
          lastMsgId = sentMsg.message_id;
          
          // Small delay between parts to maintain order
          if (messageParts.length > 1) {
            await new Promise(resolve => setTimeout(resolve, 100));
          }
        }

        // Handle images if present
        const imageUrls = [];
        if (images && Array.isArray(images) && images.length > 0) {
          for (const imageData of images) {
            try {
              // Extract base64 data (handle both with and without data URI prefix)
              let base64Data = imageData;
              if (imageData.includes('base64,')) {
                base64Data = imageData.split('base64,')[1];
              }
              
              // Generate unique filename
              const filename = `${uuidv4()}.png`;
              const filepath = path.join(uploadsDir, filename);
              
              // Save image
              fs.writeFileSync(filepath, Buffer.from(base64Data, 'base64'));
              
              // Generate URL
              const imageUrl = `http://localhost:${this.app.get('port') || 8080}/uploads/${filename}`;
              imageUrls.push(imageUrl);
              
              // Send image to Telegram
              await this.bot.sendPhoto(this.config.chatId, filepath);
              
              console.log(`📸 Image saved and sent: ${filename}`);
            } catch (imgError) {
              console.error('Error processing image:', imgError);
            }
          }
        }

        const sentMsg = { message_id: lastMsgId };

        // Store session mapping
        this.sessions.set(session_id, {
          instance_id,
          instance_name: instance.instance_name,
          telegram_msg_id: sentMsg.message_id,
          context,
          timestamp: Date.now(),
          message: message,
          imageUrls: imageUrls
        });

        // Store message thread mapping
        this.messageThreads.set(sentMsg.message_id, session_id);

        console.log(`📤 Sent to Telegram: ${instance.instance_name} → Session ${session_id.substring(0, 8)}`);
        if (imageUrls.length > 0) {
          console.log(`   📸 Images: ${imageUrls.length} sent`);
        }
        
        res.json({ 
          status: 'sent', 
          telegram_msg_id: sentMsg.message_id,
          session_id,
          imageUrls: imageUrls
        });

      } catch (error) {
        console.error('Error sending to Telegram:', error);
        res.status(500).json({ error: error.message });
      }
    });

    // Health check
    this.app.get('/health', (req, res) => {
      res.json({ 
        status: 'healthy',
        active_instances: this.instances.size,
        active_sessions: this.sessions.size,
        message_threads: this.messageThreads.size,
        uptime: process.uptime()
      });
    });

    // List active sessions
    this.app.get('/sessions', (req, res) => {
      const sessions = Array.from(this.sessions.entries()).map(([id, data]) => ({
        session_id: id,
        instance_name: data.instance_name,
        age_seconds: Math.floor((Date.now() - data.timestamp) / 1000),
        message_preview: data.message.substring(0, 50)
      }));
      res.json({ sessions, total: sessions.length });
    });

    // List registered instances
    this.app.get('/instances', (req, res) => {
      const instances = Array.from(this.instances.entries()).map(([id, data]) => ({
        instance_id: id,
        instance_name: data.instance_name,
        port: data.port,
        last_seen_seconds_ago: Math.floor((Date.now() - data.last_seen) / 1000),
        registered_at: new Date(data.registered_at).toISOString()
      }));
      res.json({ instances, total: instances.length });
    });
  }

  setupTelegramHandlers() {
    // Handle regular messages (replies)
    this.bot.on('message', async (msg) => {
      // Skip if it's a command
      if (msg.text?.startsWith('/')) return;

      const hasPhoto = msg.photo && msg.photo.length > 0;
      const mediaGroupId = msg.media_group_id;
      
      // If part of media group (album), buffer it
      if (mediaGroupId) {
        console.log(`📨 Received message (media group ${mediaGroupId.substring(0, 8)}): photos=${hasPhoto ? msg.photo.length : 0}`);
        this.bufferMediaGroupMessage(msg);
        return;
      }
      
      // Single message - process immediately
      console.log(`📨 Received single message: text=${msg.text ? true : false}, photos=${hasPhoto ? msg.photo.length : 0}`);
      await this.processMessage(msg);
    });

    // Command: List active sessions
    this.bot.onText(/\/list/, async (msg) => {
      const sessions = Array.from(this.sessions.entries())
        .sort((a, b) => b[1].timestamp - a[1].timestamp)
        .slice(0, 10);

      if (sessions.length === 0) {
        await this.bot.sendMessage(msg.chat.id, 'No active sessions');
        return;
      }

      let response = '*Active Sessions:*\n\n';
      sessions.forEach(([id, data], idx) => {
        const age = Math.floor((Date.now() - data.timestamp) / 1000);
        response += `${idx + 1}. \`${data.instance_name}\`\n`;
        response += `   Session: \`${id.substring(0, 8)}...\`\n`;
        response += `   Age: ${age}s ago\n`;
        response += `   Message: "${data.message.substring(0, 40)}..."\n\n`;
      });

      await this.bot.sendMessage(msg.chat.id, response, { parse_mode: 'Markdown' });
    });

    // Command: Show router stats
    this.bot.onText(/\/stats/, async (msg) => {
      const instances = Array.from(this.instances.entries()).map(([id, data]) => 
        `• ${data.instance_name} (port ${data.port}) - last seen ${Math.floor((Date.now() - data.last_seen) / 1000)}s ago`
      ).join('\n');

      const stats = `
*Router Statistics*

📊 Active Instances: ${this.instances.size}
💬 Active Sessions: ${this.sessions.size}
🔗 Tracked Threads: ${this.messageThreads.size}
⏱ Uptime: ${Math.floor(process.uptime())}s

*Instances:*
${instances || 'None registered'}
      `;
      await this.bot.sendMessage(msg.chat.id, stats.trim(), { parse_mode: 'Markdown' });
    });

    // Command: Help
    this.bot.onText(/\/help/, async (msg) => {
      const help = `
*Telegram-MCP Router Commands*

/list - Show active sessions
/stats - Show router statistics  
/help - Show this help message

*How to reply:*
1. Reply directly to a message (recommended)
2. Use: \`/r <session_id> <your message>\`
3. Just send a message (uses most recent session)
      `;
      await this.bot.sendMessage(msg.chat.id, help.trim(), { parse_mode: 'Markdown' });
    });

    // Handle inline keyboard button clicks  
    this.bot.on('callback_query', (callbackQuery) => {
      // Reserved for future use
      this.bot.answerCallbackQuery(callbackQuery.id);
    });
  }

  bufferMediaGroupMessage(msg) {
    const mediaGroupId = msg.media_group_id;
    
    // Get or create media group buffer
    if (!this.mediaGroups.has(mediaGroupId)) {
      this.mediaGroups.set(mediaGroupId, {
        messages: [],
        timer: null
      });
    }
    
    const group = this.mediaGroups.get(mediaGroupId);
    group.messages.push(msg);
    
    // Clear existing timer
    if (group.timer) {
      clearTimeout(group.timer);
    }
    
    // Set new timer - process after 500ms of silence
    group.timer = setTimeout(async () => {
      console.log(`   📦 Processing media group ${mediaGroupId.substring(0, 8)} (${group.messages.length} messages)`);
      await this.processMediaGroup(group.messages);
      this.mediaGroups.delete(mediaGroupId);
    }, 500);
    
    console.log(`   ⏱️  Buffered message ${group.messages.length} (timer reset)`);
  }

  async processMediaGroup(messages) {
    // Use first message for session detection and text
    const firstMsg = messages[0];
    
    // Collect all images from all messages
    const allImageUrls = [];
    for (const msg of messages) {
      if (msg.photo && msg.photo.length > 0) {
        try {
          const photo = msg.photo[msg.photo.length - 1];
          const fileId = photo.file_id;
          
          const fileLink = await this.bot.getFileLink(fileId);
          const response = await axios.get(fileLink, { responseType: 'arraybuffer' });
          
          const filename = `${uuidv4()}.jpg`;
          const filepath = path.join(uploadsDir, filename);
          fs.writeFileSync(filepath, response.data);
          
          const imageUrl = `http://localhost:${this.app.get('port') || 8080}/uploads/${filename}`;
          allImageUrls.push(imageUrl);
          
          console.log(`   ✅ Photo saved: ${filename}`);
        } catch (error) {
          console.error(`   ❌ Error processing photo:`, error);
        }
      }
    }
    
    await this.processMessage(firstMsg, allImageUrls);
  }

  async processMessage(msg, preProcessedImages = null) {
    const chatId = msg.chat.id;
    let session_id = null;

    // Method 1: Check if this is a reply to a previous message
    if (msg.reply_to_message) {
      const repliedToId = msg.reply_to_message.message_id;
      session_id = this.messageThreads.get(repliedToId);
      
      if (session_id) {
        console.log(`   ✓ Reply detected via thread: ${session_id.substring(0, 8)}`);
      }
    }

    // Method 2: Extract session_id from message text
    if (!session_id && msg.text) {
      const match = msg.text.match(/\/r\s+([a-f0-9-]+)\s+(.*)/i);
      if (match) {
        session_id = match[1];
        msg.text = match[2];
        console.log(`   ✓ Reply detected via /r command: ${session_id.substring(0, 8)}`);
      }
    }

    // Method 3: Use most recent session
    if (!session_id) {
      session_id = this.getMostRecentSession();
      if (session_id) {
        console.log(`   ⚠ Using most recent session: ${session_id.substring(0, 8)}`);
      }
    }

    if (!session_id) {
      await this.bot.sendMessage(
        chatId,
        '❌ No active session found. Please reply to a specific message or use /list to see active sessions.'
      );
      return;
    }

    // Process photos if not already processed
    let imageUrls = preProcessedImages || [];
    if (!preProcessedImages && msg.photo && msg.photo.length > 0) {
      try {
        const photo = msg.photo[msg.photo.length - 1];
        const fileId = photo.file_id;
        
        console.log(`   📸 Processing photo: ${fileId}`);
        
        const fileLink = await this.bot.getFileLink(fileId);
        const response = await axios.get(fileLink, { responseType: 'arraybuffer' });
        
        const filename = `${uuidv4()}.jpg`;
        const filepath = path.join(uploadsDir, filename);
        fs.writeFileSync(filepath, response.data);
        
        const imageUrl = `http://localhost:${this.app.get('port') || 8080}/uploads/${filename}`;
        imageUrls.push(imageUrl);
        
        console.log(`   ✅ Photo saved: ${filename}`);
      } catch (error) {
        console.error(`   ❌ Error processing photo:`, error);
      }
    }

    // Route to instance
    await this.routeToInstance(session_id, msg.text || msg.caption || '', imageUrls, chatId);
  }

  async routeToInstance(session_id, message, imageUrls, chatId) {
    const session = this.sessions.get(session_id);
    
    if (!session) {
      await this.bot.sendMessage(chatId, `❌ Session ${session_id.substring(0, 8)} not found or expired`);
      return;
    }

    const instance = this.instances.get(session.instance_id);
    
    if (!instance) {
      await this.bot.sendMessage(chatId, `❌ Instance for session not found`);
      return;
    }

    try {
      const hasText = message && message.trim().length > 0;
      const hasImages = imageUrls && imageUrls.length > 0;
      
      console.log(`🔀 Routing to ${instance.instance_name}:`);
      console.log(`   Text: "${hasText ? message : '(none)'}"`);
      console.log(`   Images: ${hasImages ? imageUrls.length : 0}`);
      
      // Forward reply to the MCP instance
      const response = await axios.post(instance.callback_url, {
        session_id,
        message,
        image_urls: imageUrls || [],
        context: session.context,
        timestamp: Date.now()
      }, {
        timeout: 10000 // 10 second timeout
      });

      console.log(`   ✅ Successfully delivered to ${instance.instance_name}`);
      
      // Send confirmation to Telegram
      await this.bot.sendMessage(
        chatId,
        `✅ Sent to *${instance.instance_name}*`,
        { parse_mode: 'Markdown' }
      );

      // Clean up session after successful delivery
      this.sessions.delete(session_id);
      this.messageThreads.delete(session.telegram_msg_id);

    } catch (error) {
      console.error(`   ❌ Error routing to instance:`, error.message);
      await this.bot.sendMessage(
        chatId,
        `❌ Failed to deliver to ${instance.instance_name}: ${error.message}`
      );
    }
  }

  formatOutgoingMessage(instanceName, message, session_id) {
    const MAX_LENGTH = 4000;
    
    // Clean up message - remove unwanted elements
    let cleanMessage = message
      // Remove datetime stamps
      .replace(/⏰\s+\w+\s+\d+,\s+\d+:\d+/g, '')
      // Remove file paths
      .replace(/📁\s+[A-Z]:\\[^\n]+/g, '')
      // Remove emoji headers like "🔔 Feedback Request • "
      .replace(/🔔\s+Feedback Request\s+•\s+/g, '')
      // Remove footers with session info, links, etc
      .replace(/━+[\s\S]*?Session ID:.*$/gm, '')
      .replace(/✅\s+What to do next:[\s\S]*$/gm, '')
      .replace(/🔗\s+Open Feedback Interface.*$/gm, '')
      // Remove truncation messages
      .replace(/\(Summary truncated.*?\)/g, '')
      .trim();
    
    const parts = [];
    
    // If message fits in one part
    if (cleanMessage.length <= MAX_LENGTH) {
      return [{
        text: `*${instanceName}*\n\n${cleanMessage}`,
        session_id: session_id
      }];
    }
    
    // Split into chunks
    let remaining = cleanMessage;
    while (remaining.length > 0) {
      let chunk;
      if (remaining.length <= MAX_LENGTH) {
        chunk = remaining;
        remaining = '';
      } else {
        let splitPos = MAX_LENGTH;
        const sentenceEnd = remaining.lastIndexOf('. ', MAX_LENGTH);
        const lineEnd = remaining.lastIndexOf('\n', MAX_LENGTH);
        const spacePos = remaining.lastIndexOf(' ', MAX_LENGTH);
        
        if (sentenceEnd > MAX_LENGTH * 0.7) {
          splitPos = sentenceEnd + 1;
        } else if (lineEnd > MAX_LENGTH * 0.7) {
          splitPos = lineEnd + 1;
        } else if (spacePos > MAX_LENGTH * 0.7) {
          splitPos = spacePos + 1;
        }
        
        chunk = remaining.substring(0, splitPos).trim();
        remaining = remaining.substring(splitPos).trim();
      }
      parts.push(chunk);
    }
    
    // Format each part
    return parts.map((chunk, index) => {
      const isFirst = index === 0;
      
      let text = '';
      if (isFirst) text += `*${instanceName}*\n\n`;
      text += chunk;
      
      return {
        text: text,
        session_id: session_id
      };
    });
  }

  getMostRecentSession() {
    if (this.sessions.size === 0) return null;
    
    let mostRecent = null;
    let latestTime = 0;
    
    for (const [id, data] of this.sessions.entries()) {
      if (data.timestamp > latestTime) {
        latestTime = data.timestamp;
        mostRecent = id;
      }
    }
    
    return mostRecent;
  }

  startServer(port) {
    this.app.listen(port, () => {
      console.log('═══════════════════════════════════════');
      console.log('🚀 Telegram Router Started Successfully');
      console.log('═══════════════════════════════════════');
      console.log(`📡 HTTP Server: http://localhost:${port}`);
      console.log(`📱 Telegram Bot: Connected`);
      console.log(`💬 Chat ID: ${this.config.chatId}`);
      console.log('═══════════════════════════════════════');
      console.log('Ready to route messages! 🎯\n');
    });
  }

  startCleanupTask() {
    // Cleanup old sessions every interval
    setInterval(() => {
      const now = Date.now();
      let cleaned = 0;
      
      for (const [id, data] of this.sessions.entries()) {
        if (now - data.timestamp > this.config.sessionMaxAge) {
          this.sessions.delete(id);
          this.messageThreads.delete(data.telegram_msg_id);
          cleaned++;
        }
      }
      
      if (cleaned > 0) {
        console.log(`🧹 Cleaned up ${cleaned} expired sessions`);
      }
    }, this.config.sessionCleanupInterval);
  }
}

// Start the router
const router = new TelegramRouter(
  process.env.TELEGRAM_BOT_TOKEN,
  parseInt(process.env.ROUTER_PORT) || 8080
);

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\n🛑 Shutting down router gracefully...');
  process.exit(0);
});

module.exports = TelegramRouter;
