const express = require("express");
const { WebClient } = require("@slack/web-api");
const { createEventAdapter } = require("@slack/events-api");
const dotenv = require("dotenv");
const axios = require("axios");

dotenv.config();

const app = express();
const port = 3000;

const slackSigningSecret = process.env.SLACK_SIGNING_SECRET;
const slackToken = process.env.SLACK_BOT_TOKEN;

let slackEvents;
let slackClient;

try {
  slackEvents = createEventAdapter(slackSigningSecret, {
    includeBody: true,
    includeHeaders: true
  });
  slackClient = new WebClient(slackToken);
  console.log("Slack API initialized successfully");
} catch (error) {
  console.error("Error initializing Slack API:", error);
}

const rawBodyBuffer = (req, res, buf, encoding) => {
  if (buf && buf.length) {
    req.rawBody = buf.toString(encoding || 'utf8');
  }
};

app.use('/slack/events', express.raw({type: 'application/json', verify: rawBodyBuffer}));

app.use('/slack/events', (req, res, next) => {
  console.log('Request received at /slack/events');
  console.log('Headers:', req.headers);
  console.log('Body:', req.body);
  next();
}, slackEvents.expressMiddleware());

slackEvents.on('error', (error) => {
  console.error('Slack events error:', error);
});

slackEvents.on('message', async (event) => {
  console.log('Message event received:', event);
  try {
    if (!event.bot_id) {
      console.log("Processing message:", event.text);
      const response = await processMessageAndCallAPI(event.text);
      console.log("response:", response);

      await slackClient.chat.postMessage({
        channel: event.channel,
        text: response.response,
      });
      console.log("Response sent to Slack");
    }
  } catch (error) {
    console.error("Error handling message event:", error);
  }
});

async function processMessageAndCallAPI(message) {
  try {
    const response = await axios.post(`${process.env.FLASK_API_URL}`, {
      message,
    });
    console.log("API response:", response.data);
    return response.data;
  } catch (error) {
    console.error("Error calling Flask API:", error);
    return "Sorry, there was an error processing your request.";
  }
}

app.post('/slack/events', (req, res) => {
  if (req.body && req.body.type === 'url_verification') {
    console.log('Received url_verification request');
    return res.json({ challenge: req.body.challenge });
  }
  slackEvents.handle(req, res);
});

app.get('/test', (req, res) => {
  console.log('Test endpoint hit');
  res.send('Server is running');
});

app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).send('Something broke!');
});

app.listen(port, () => {
  console.log(`Slack bot is listening at http://localhost:${port}`);
});