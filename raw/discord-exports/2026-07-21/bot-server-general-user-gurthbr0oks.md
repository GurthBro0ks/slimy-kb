---
title: "general — messages by gurthbr0oks export"
guild: "Bot_Server"
guild_id: "1470115970684026963"
channel: "general"
channel_id: "1470115973032968225"
exported_at: "2026-07-21T14:10:36.011Z"
exported_by: "gurthbr0oks"
message_count: 40
date_range: "2026-02-08T20:54:47.391Z .. 2026-07-21T14:03:49.808Z"
filtered_user: "gurthbr0oks"
filtered_user_id: "427999592986968074"
total_scanned: 40
tags: [discord-export, channel/general, guild/bot-server, user/gurthbr0oks]
---

# general — messages by gurthbr0oks

## 2026-02-08

**Gurth Brooks** (`gurthbr0oks`) · 20:54:47 UTC
> <@1465018485271691285> ping
^msg-1470160961078825061

**Gurth Brooks** (`gurthbr0oks`) · 20:57:26 UTC
> Execute this:
> execute this <@1465018485271691285> 
> // FILE: discord-server-setup.js
> // PURPOSE: Orchestrator bot initializes Discord server structure
> // RUN: node discord-server-setup.js
> 
> const { Client, GatewayIntentBits, ChannelType, PermissionFlagsBits } = require('discord.js');
> 
> const config = {
>   botToken: process.env.ORCHESTRATOR\_TOKEN,
>   serverId: process.env.DISCORD\_SERVER\_ID
> };
> 
> const serverStructure = {
>   roles: [
>     { name: '🎯 Orchestrator', color: '#FF0000', permissions: ['Administrator'] },
>     { name: '🤖 Worker Bot', color: '#00FF00', permissions: ['SendMessages', 'ReadMessageHistory'] },
>     { name: '👁️ Observer', color: '#0000FF', permissions: ['ViewChannel'] }
>   ],
>   categories: [
>     {
>       name: '📊 CONTROL CENTER',
>       channels: [
>         { name: '📋-orchestrator-commands', type: 'text' },
>         { name: '📊-system-status', type: 'text' },
>         { name: '🔔-notifications', type: 'text' }
>       ]
>     },
>     {
>       name: '⚙️ TASK EXECUTION',
>       channels: [
>         { name: '📥-task-queue', type: 'text' },
>         { name: '🔄-in-progress', type: 'text' },
>         { name: '✅-completed', type: 'text' },
>         { name: '❌-failed', type: 'text' }
>       ]
>     },
>     {
>       name: '🤖 WORKER CHANNELS',
>       channels: [
>         { name: '🤖-worker-1', type: 'text' },
>         { name: '🤖-worker-2', type: 'text' },
>         { name: '🤖-worker-3', type: 'text' }
>       ]
>     },
>     {
>       name: '📝 LOGS & MONITORING',
>       channels: [
>         { name: '📝-orchestrator-logs', type: 'text' },
>         { name: '🔍-worker-logs', type: 'text' },
>         { name: '⏱️-performance-metrics', type: 'text' }
>       ]
>     }
>   ]
> };
> 
> async function setupServer() {
>   const client = new Client({
>     intents: [
>       GatewayIntentBits.Guilds,
>       GatewayIntentBits.GuildMessages,
>       GatewayIntentBits.MessageContent
>     ]
>   });
> 
>   await client.login(config.botToken);
>   
>   client.once('ready', async () => {
>     console.log(\`Logged in as ${client.user.tag}\`);
>     
>     const guild = await client.guilds.fetch(config.serverId);
>     
>     // CREATE ROLES
>     console.log('Creating roles...');
>     const roleMap = {};
>     for (const roleConfig of serverStructure.roles) {
>       const role = await guild.roles.create({
>         name: roleConfig.name,
>         color: roleConfig.color,
>         permissions: roleConfig.permissions
>       });
>       roleMap[roleConfig.name] = role;
>       console.log(\`✓ Created role: ${roleConfig.name}\`);
>     }
>     
>     // CREATE CATEGORIES & CHANNELS
>     console.log('\nCreating categories and channels...');
>     for (const categoryConfig of serverStructure.categories) {
>       const category = await guild.channels.create({
>         name: categoryConfig.name,
>         type: ChannelType.GuildCategory
>       });
>       console.log(\`✓ Created category: ${categoryConfig.name}\`);
>       
>       for (const channelConfig of categoryConfig.channels) {
>         const channel = await guild.channels.create({
>           name: channelConfig.name,
>           type: channelConfig.type === 'text' ? ChannelType.GuildText : ChannelType.GuildVoice,
>           parent: category.id
>         });
>         console.log(\`  ✓ Created channel: ${channelConfig.name}\`);
>       }
>     }
>     
>     console.log('\n✅ Server setup complete!');
>     console.log('\nNext steps:');
>     console.log('1. Invite worker bots with this URL:');
>     console.log('   https://discord.com/api/oauth2/authorize?client\_id=YOUR\_BOT\_ID&permissions=2048&scope=bot');
>     console.log('2. Assign "🤖 Worker Bot" role to each worker bot');
>     console.log('3. Start Phase 2: Orchestration Logic');
>     
>     process.exit(0);
>   });
> }
> 
> setupServer().catch(console.error);
^msg-1470161626400555032

**Gurth Brooks** (`gurthbr0oks`) · 21:00:01 UTC
> I approve of you to run it in this server. Your token is the orchestrator token
^msg-1470162276677062686

## 2026-02-09

**Gurth Brooks** (`gurthbr0oks`) · 00:48:24 UTC
> <@1465018485271691285> please execute this:
> Create .env file:
> 
> bash   ORCHESTRATOR\_TOKEN=your\_orchestrator\_bot\_token
>    DISCORD\_SERVER\_ID=your\_server\_id
> 
> Run: npm install discord.js && node discord-server-setup.js
^msg-1470219754294743243

**Gurth Brooks** (`gurthbr0oks`) · 00:52:40 UTC
> <@1465018485271691285> update the correct file to include WORKER\_1\_TOKEN=MTQ3MDEyMTM2Mjg4OTc2OTA3NA.GyjpGP.23Km1uVxaEN4CXUraGsrW1BkCYq-b9LNIGpro8
> 
> That is Ned's token. he will be our first worker
^msg-1470220828305260751

**Gurth Brooks** (`gurthbr0oks`) · 00:53:06 UTC
> // FILE: create-worker-bot.js
> // PURPOSE: Generate worker bot application on Discord Developer Portal
> // NOTE: Discord API doesn't support bot creation via API - must do manually
> 
> console.log(\`
> WORKER BOT CREATION CHECKLIST:
> ===============================
> 
> For EACH worker bot (Worker 1, Worker 2, Worker 3):
> 
> 1. Go to: https://discord.com/developers/applications
> 2. Click "New Application"
> 3. Name: "Agent Worker 1" (or 2, 3)
> 4. Navigate to "Bot" section
> 5. Click "Add Bot"
> 6. Enable these Privileged Gateway Intents:
>    ☑ MESSAGE CONTENT INTENT
>    ☑ SERVER MEMBERS INTENT (optional)
>    ☑ PRESENCE INTENT (optional)
> 7. Copy bot token → Save to .env as WORKER\_1\_TOKEN
> 8. Navigate to OAuth2 > URL Generator
> 9. Select scopes: "bot"
> 10. Select permissions: "Send Messages", "Read Message History"
> 11. Copy generated URL
> 12. Paste URL in browser → Select your server → Authorize
> 
> Invite URLs will look like:
> https://discord.com/api/oauth2/authorize?client\_id=WORKER\_BOT\_CLIENT\_ID&permissions=3072&scope=bot
> 
> After inviting all bots, update .env:
> WORKER\_1\_TOKEN=...
> WORKER\_2\_TOKEN=...
> WORKER\_3\_TOKEN=...
> \`);
^msg-1470220936744669328

**Gurth Brooks** (`gurthbr0oks`) · 00:53:31 UTC
> disregard most of that. I made Ned's bot already
^msg-1470221039865827378

**Gurth Brooks** (`gurthbr0oks`) · 00:57:17 UTC
> \#!/bin/bash
> \# FILE: /home/jason/discord-orchestrator/setup-project.sh
> \# PURPOSE: Initialize the Discord orchestrator project
> \# RUN: bash setup-project.sh
> 
> PROJECT\_DIR="/home/jason/discord-orchestrator"
> 
> echo "🚀 Setting up Discord Orchestrator Project..."
> 
> \# CREATE PROJECT DIRECTORY
> mkdir -p $PROJECT\_DIR
> cd $PROJECT\_DIR
> 
> \# CREATE SUBDIRECTORIES
> mkdir -p logs
> mkdir -p backups
> 
> \# CREATE .env FILE
> cat > .env << 'EOF'
> \# ===== DISCORD BOT TOKENS =====
> ORCHESTRATOR\_TOKEN=
> WORKER\_1\_TOKEN=
> WORKER\_2\_TOKEN=
> WORKER\_3\_TOKEN=
> 
> \# ===== DISCORD SERVER =====
> DISCORD\_SERVER\_ID=
> 
> \# ===== OPENCLAW CONFIGURATION =====
> NUC1\_HOST=localhost
> NUC1\_PORT=3000
> NUC2\_HOST=192.168.1.101
> NUC2\_PORT=3000
> 
> \# ===== OPENCLAW GATEWAY =====
> OPENCLAW\_GATEWAY\_URL=http://localhost:8080
> OPENCLAW\_API\_KEY=
> 
> \# ===== REDIS (optional) =====
> REDIS\_HOST=localhost
> REDIS\_PORT=6379
> 
> \# ===== LOGGING =====
> LOG\_LEVEL=info
> LOG\_FILE=/home/jason/discord-orchestrator/logs/orchestrator.log
> EOF
> 
> \# CREATE package.json
> cat > package.json << 'EOF'
> {
>   "name": "discord-orchestrator",
>   "version": "1.0.0",
>   "description": "Multi-agent Discord orchestration system for OpenClaw",
>   "main": "orchestrator.js",
>   "scripts": {
>     "start": "node orchestrator.js",
>     "setup-server": "node discord-server-setup.js",
>     "dev": "nodemon orchestrator.js"
>   },
>   "dependencies": {
>     "discord.js": "^14.14.1",
>     "dotenv": "^16.3.1",
>     "redis": "^4.6.11",
>     "axios": "^1.6.2"
>   },
>   "devDependencies": {
>     "nodemon": "^3.0.2"
>   }
> }
> EOF
> 
> \# CREATE .gitignore
> cat > .gitignore << 'EOF'
> node\_modules/
> .env
> logs/\*.log
> backups/
> \*.sqlite
> \*.db
> EOF
> 
> \# INSTALL DEPENDENCIES
> npm install
> 
> \# SET PERMISSIONS
> chmod 600 .env
> chmod +x \*.sh
> 
> echo "✅ Project structure created at: $PROJECT\_DIR"
> echo ""
> echo "📋 Next steps:"
> echo "1. Edit .env and add your Discord bot tokens"
> echo "2. Run: node discord-server-setup.js"
> echo "3. Run: node orchestrator.js"
> echo ""
> echo "⚠️  SECURITY NOTE: .env contains secrets - never commit to git!"
^msg-1470221986612510896

**Gurth Brooks** (`gurthbr0oks`) · 01:00:27 UTC
> yes
^msg-1470222784037654528

**Gurth Brooks** (`gurthbr0oks`) · 01:01:32 UTC
> also make sure your token is in the orchestrator spot
^msg-1470223059511283753

**Gurth Brooks** (`gurthbr0oks`) · 01:03:04 UTC
> your token is the orchestrator token
^msg-1470223443835355247

**Gurth Brooks** (`gurthbr0oks`) · 01:03:33 UTC
> execute this:
- 📎 [message.txt](https://cdn.discordapp.com/attachments/1470115973032968225/1470223566862811187/message.txt?ex=6a60bfa5&is=6a5f6e25&hm=aabcd39f9cd4faac13cd3db045573b889e6061c7bc13ba8a034f9e77a4099eb1&)
^msg-1470223566367621380

**Gurth Brooks** (`gurthbr0oks`) · 01:04:35 UTC
> here: MTQ2NTAxODQ4NTI3MTY5MTI4NQ.Gabgwb.\_gA4rD58G7aGNSYEms4Gmga0kQWLBJqtR\_tovw
^msg-1470223826515263609

**Gurth Brooks** (`gurthbr0oks`) · 01:08:35 UTC
> oooh i get it. so is ned not needed either? Im confused
^msg-1470224832065966162

**Gurth Brooks** (`gurthbr0oks`) · 01:48:44 UTC
> So what do you do
^msg-1470234938333724936

**Gurth Brooks** (`gurthbr0oks`) · 11:05:18 UTC
> So I need to make more discord bots
^msg-1470375000736530558

**Gurth Brooks** (`gurthbr0oks`) · 11:09:03 UTC
> Do we need Ned and you? Your token is in the orchestrator spot and Ned’s is in worker 1
^msg-1470375943838240770

**Gurth Brooks** (`gurthbr0oks`) · 16:36:10 UTC
> So how do they run if you’re not doing it. Do you spawn agents onto them?
^msg-1470458267791659111

## 2026-02-11

**Gurth Brooks** (`gurthbr0oks`) · 03:06:04 UTC
> <@1465018485271691285> ping
^msg-1470979174809473185

**Gurth Brooks** (`gurthbr0oks`) · 03:06:48 UTC
> execute this please:
> \# ---- Test remote (Ned on NUC1) ----
> echo "Testing connectivity to Ned (NUC1)..."
> if nc -zw3 192.168.68.64 18789 2>/dev/null; then
>     REMOTE\_HTTP=$(curl -sS -o /dev/null -w "%{http\_code}" --connect-timeout 5 \
>       -X POST "http://192.168.68.64:18789/hooks/wake" \
>       -H "Authorization: Bearer bridge-n1-a7f3c9e2b8d14506" \
>       -H "Content-Type: application/json" \
>       -d '{"text":"Bridge test from Chriss","mode":"now"}' 2>/dev/null \|\| echo "000")
> 
>     if [[ "$REMOTE\_HTTP" == "200" ]]; then
>         echo "✓ Cross-NUC webhook test: PASSED! 🎉"
>     elif [[ "$REMOTE\_HTTP" == "401" ]]; then
>         echo "⚠️ Ned reachable but auth failed - did you run setup-nuc1.sh?"
>     else
>         echo "⚠️ Ned returned HTTP $REMOTE\_HTTP"
>     fi
> else
>     echo "⚠️ Ned port 18789 not reachable - run setup-nuc1.sh on NUC1 first"
> fi
> 
> echo ""
> echo "=== NUC2 (Chriss) DONE ==="
> echo ""
> echo "TEST THE FULL BRIDGE:"
> echo "  From NUC2: \~/send-to-ned.sh 'Hello from Chriss!'"
> echo "  From NUC1: \~/send-to-chriss.sh 'Hello from Ned!'"
> echo ""
> echo "TRADING WORKFLOW EXAMPLES:"
> echo ""
> echo "  # Chriss tells Ned to run a Kalshi scan:"
> echo "  \~/send-to-ned.sh 'Run Kalshi YES+NO sum scanner and report any arbs under 0.97'"
> echo ""
> echo "  # Chriss tells Ned to start optimization:"
> echo "  \~/send-to-ned.sh 'Start Ned optimization cycle' 'hook:ned:optimize'"
> echo ""
> echo "  # Chriss asks Ned to check IBKR:"
> echo "  \~/send-to-ned.sh 'Check IBKR positions and P&L for today'"
> echo ""
> echo "  # From inside Chriss's agent session (exec tool):"
> echo "  # bash \~/send-to-ned.sh 'Run parameter sweep on edge thresholds'"
> echo ""
> echo "  # Ned (NUC1) reports back to Chriss automatically via:"
> echo "  # \~/send-to-chriss.sh 'Arb found: KXBTC YES=0.52 NO=0.44 sum=0.96 edge=4.2%'"
^msg-1470979356523233424

## 2026-02-18

**Gurth Brooks** (`gurthbr0oks`) · 01:09:56 UTC
> <@1470121362889769074> ping
^msg-1473486662699843678

## 2026-02-28

**Gurth Brooks** (`gurthbr0oks`) · 18:23:02 UTC
> ● Summary                                                
> 
>   The Floor 2 fixes have been implemented in the source code:                   
>   
>   Fix: Wake Button                                                              
>   Status: ✅ Code Fixed                                           
>   Notes: Changed to "Wake Chriss" - needs service restart
>   ────────────────────────────────────────
>   Fix: Agent Movement
>   Status: ✅ Already working
>   Notes: Logic exists in PixelOffice.tsx
>   ────────────────────────────────────────
>   Fix: Memory Path
>   Status: ✅ Fixed
>   Notes: Removed logs directory from MEMORY\_DIRS
>   ────────────────────────────────────────
>   Fix: Scoreboard
>   Status: ✅ Already working
>   Notes: 41 tasks this week
> 
>   Files Modified:
>   1. /home/slimy/mission-control/app/ops/page.tsx - Wake Chriss button
>   2. /home/slimy/mission-control/app/api/memory/route.ts - Removed logs
^msg-1477370528099471585

**Gurth Brooks** (`gurthbr0oks`) · 18:23:20 UTC
> ● Fixed! The changes are now live:                                              
>                                                                                 
>   - "⚡ Wake Chriss" ✅                                                         
>   - "🔵 Ping Floor 1" ✅ (was "Test Discord")                                   
>                                                                                 
>   All Floor 2 fixes are now applied.                                            
> 
> ✻ Brewed for 50s
^msg-1477370603966173246

**Gurth Brooks** (`gurthbr0oks`) · 18:25:57 UTC
> Floor 2 agents are not moving and scoreboard still shows 0
^msg-1477371265579880489

## 2026-04-25

**Gurth Brooks** (`gurthbr0oks`) · 11:44:20 UTC
> <@1470142627017134151> dispatch
^msg-1497563912235647046

**Gurth Brooks** (`gurthbr0oks`) · 11:44:48 UTC
> <@1470142627017134151> pause
^msg-1497564033547636826

**Gurth Brooks** (`gurthbr0oks`) · 11:45:03 UTC
> <@1470142627017134151> resume
^msg-1497564096160337920

**Gurth Brooks** (`gurthbr0oks`) · 11:45:20 UTC
> <@1470142627017134151> reset counter
^msg-1497564166221725716

## 2026-05-22

**Gurth Brooks** (`gurthbr0oks`) · 18:30:40 UTC
> <a:barf:1507450543205908590>
^msg-1507450645161054382

## 2026-06-30

**Gurth Brooks** (`gurthbr0oks`) · 21:38:20 UTC
> 
- 📎 [IMG\_8269.png](https://cdn.discordapp.com/attachments/1470115973032968225/1521630999409328168/IMG_8269.png?ex=6a608f8c&is=6a5f3e0c&hm=d2e32394c971baf2cf0d00c338c2225542698fd781f1fe8bbac1e8acc56df64e&)
^msg-1521630999849467925

## 2026-07-03

**Gurth Brooks** (`gurthbr0oks`) · 16:58:45 UTC
> 
- 📎 [IMG\_8269.png](https://cdn.discordapp.com/attachments/1470115973032968225/1522647797143310346/IMG_8269.png?ex=6a604e04&is=6a5efc84&hm=30e91e9b8c96a1d00a829b4abe79939f24559fd8e51a13594d6b058cb37501da&)
- 📎 [IMG\_8270.png](https://cdn.discordapp.com/attachments/1470115973032968225/1522647797550022706/IMG_8270.png?ex=6a604e04&is=6a5efc84&hm=edf4040845ad710cdfbd2137c86b20d11019b19a4a916f9b00cac7c8a1d68254&)
- 📎 [IMG\_8271.png](https://cdn.discordapp.com/attachments/1470115973032968225/1522647797944549596/IMG_8271.png?ex=6a604e04&is=6a5efc84&hm=b3c6afe282b229e69640c404e692f619288f41a8c9956f28a6f816ad8d80a4f7&)
- 📎 [IMG\_8272.png](https://cdn.discordapp.com/attachments/1470115973032968225/1522647798443409468/IMG_8272.png?ex=6a604e04&is=6a5efc84&hm=1f5866496cfee9b0cad26289e48418441ae2980f43a77ec1a94c875bc4b0b996&)
- 📎 [IMG\_8273.png](https://cdn.discordapp.com/attachments/1470115973032968225/1522647798892335104/IMG_8273.png?ex=6a604e04&is=6a5efc84&hm=79a56f370576ed01d4834bd8568a4775098b75f3ed826f8b2b074c09694a9680&)
- 📎 [IMG\_8274.png](https://cdn.discordapp.com/attachments/1470115973032968225/1522647799181873322/IMG_8274.png?ex=6a604e04&is=6a5efc84&hm=1a81a4779844184ce0c41aa3b992b759e36eecb62802463c350e08b1035b613f&)
- 📎 [IMG\_8275.png](https://cdn.discordapp.com/attachments/1470115973032968225/1522647799605493870/IMG_8275.png?ex=6a604e04&is=6a5efc84&hm=fbf771feacc0afcb8c1174c9de70b578754b0fab8f1fd5ae7e30484db5d55d2c&)
- 📎 [IMG\_8276.png](https://cdn.discordapp.com/attachments/1470115973032968225/1522647799941042246/IMG_8276.png?ex=6a604e04&is=6a5efc84&hm=5049cbf415e8c85b0c71a28852a2cbbe3b2e6742948f8debd59df0358370a7ef&)
- 📎 [IMG\_8277.png](https://cdn.discordapp.com/attachments/1470115973032968225/1522647800305815642/IMG_8277.png?ex=6a604e05&is=6a5efc85&hm=bec5e8859534a56af6cbd65228305881e0091cf19c2bc2edf69133f1648a3268&)
- 📎 [IMG\_8278.png](https://cdn.discordapp.com/attachments/1470115973032968225/1522647800687362199/IMG_8278.png?ex=6a604e05&is=6a5efc85&hm=82559f980d6db99495bc11e51070e91dab12b218e208800322fef7a2bd0a76f9&)
^msg-1522647801010589796

**Gurth Brooks** (`gurthbr0oks`) · 16:58:56 UTC
> Sim power
^msg-1522647846984089752

**Gurth Brooks** (`gurthbr0oks`) · 16:59:11 UTC
> 
- 📎 [IMG\_8259.png](https://cdn.discordapp.com/attachments/1470115973032968225/1522647908850209039/IMG_8259.png?ex=6a604e1e&is=6a5efc9e&hm=1e46adf6c4a3d5851f29678f1094445898b94cf2e38a4ddbe7a3e1c3a2379e6b&)
- 📎 [IMG\_8260.png](https://cdn.discordapp.com/attachments/1470115973032968225/1522647909240410213/IMG_8260.png?ex=6a604e1e&is=6a5efc9e&hm=772ec57e7c2eedd6b474e7dc7eea701273b72a80b7efa7619ab81661fc256566&)
- 📎 [IMG\_8261.png](https://cdn.discordapp.com/attachments/1470115973032968225/1522647909580017864/IMG_8261.png?ex=6a604e1f&is=6a5efc9f&hm=a58406b1964427ed7d6ff2325cc2b2beb721bd9936b4282ecf0dac6414e8e035&)
- 📎 [IMG\_8262.png](https://cdn.discordapp.com/attachments/1470115973032968225/1522647909932208300/IMG_8262.png?ex=6a604e1f&is=6a5efc9f&hm=29ae3a96ebe53a1e20d43a1710ca5c3b00d4db8712f51c79475c990c48b02fe1&)
- 📎 [IMG\_8263.png](https://cdn.discordapp.com/attachments/1470115973032968225/1522647910544834650/IMG_8263.png?ex=6a604e1f&is=6a5efc9f&hm=6692359d155feeee7b2a173054e80f0b99dca4a82055df6b23fd8fc8f34501c3&)
- 📎 [IMG\_8265.png](https://cdn.discordapp.com/attachments/1470115973032968225/1522647911018659971/IMG_8265.png?ex=6a604e1f&is=6a5efc9f&hm=46e737833fae53926ee97fec832f755fd475053bcaf21461394eff05f19617ae&)
- 📎 [IMG\_8264.png](https://cdn.discordapp.com/attachments/1470115973032968225/1522647911341756581/IMG_8264.png?ex=6a604e1f&is=6a5efc9f&hm=09a84aa0bd7bee87ae6b55a5573e3561d41834437e6d2cf97c8a4252c11d57fe&)
- 📎 [IMG\_8266.png](https://cdn.discordapp.com/attachments/1470115973032968225/1522647911702331442/IMG_8266.png?ex=6a604e1f&is=6a5efc9f&hm=8e311028c3cbdd4d1af923958d4a96c21b1c49c0fa1bab61543216984f549495&)
- 📎 [IMG\_8267.png](https://cdn.discordapp.com/attachments/1470115973032968225/1522647912096469032/IMG_8267.png?ex=6a604e1f&is=6a5efc9f&hm=de23a2298cc95bb39a95024186cd0b4c45bb1785a381022555dfbe78aa2e43e3&)
- 📎 [IMG\_8268.png](https://cdn.discordapp.com/attachments/1470115973032968225/1522647912407105727/IMG_8268.png?ex=6a604e1f&is=6a5efc9f&hm=ad56d97fe16aa833960230a02a90a761d10a3fba64d854477145f98da272bfcf&)
^msg-1522647912662827138

**Gurth Brooks** (`gurthbr0oks`) · 16:59:17 UTC
> Total power
^msg-1522647934653567150

## 2026-07-09

**Gurth Brooks** (`gurthbr0oks`) · 16:35:54 UTC
> 
- 📎 [IMG\_8540.png](https://cdn.discordapp.com/attachments/1470115973032968225/1524816377393844344/IMG_8540.png?ex=6a6048aa&is=6a5ef72a&hm=e57cf1b33ae9ede533ad1b7221f3b5de4d1bffb0aed6a47e8d83ff02526dc970&)
- 📎 [IMG\_8541.png](https://cdn.discordapp.com/attachments/1470115973032968225/1524816377964396584/IMG_8541.png?ex=6a6048aa&is=6a5ef72a&hm=7408db3ced0b7f7f037b8e254346c63d25f7a68a60ca81a4215b5515c19fd6bc&)
- 📎 [IMG\_8542.png](https://cdn.discordapp.com/attachments/1470115973032968225/1524816378488688741/IMG_8542.png?ex=6a6048aa&is=6a5ef72a&hm=643a909cb6f412c41afdbc1275791e84ae2ca9803137ca15a7a3198ce185913b&)
^msg-1524816378886881390

**Gurth Brooks** (`gurthbr0oks`) · 16:35:57 UTC
> 
- 📎 [IMG\_8543.png](https://cdn.discordapp.com/attachments/1470115973032968225/1524816391566266579/IMG_8543.png?ex=6a6048ad&is=6a5ef72d&hm=d58802ab10ba8c5781f450e3b60dbbba8a93e0e963e154f5feda65b96a3248d8&)
- 📎 [IMG\_8544.png](https://cdn.discordapp.com/attachments/1470115973032968225/1524816392027898096/IMG_8544.png?ex=6a6048ad&is=6a5ef72d&hm=118bd8e3fa62e4dfadeba4a08e63484824454b89e950e5cb705438677dfbb895&)
- 📎 [IMG\_8545.png](https://cdn.discordapp.com/attachments/1470115973032968225/1524816392522694726/IMG_8545.png?ex=6a6048ad&is=6a5ef72d&hm=075bf3fe9811739eb47c83446c53b5215c1eb70ed1fd0974efcb6796050999f7&)
^msg-1524816392841596959

## 2026-07-21

**Gurth Brooks** (`gurthbr0oks`) · 14:03:22 UTC
> 
- 📎 [IMG\_8873.png](https://cdn.discordapp.com/attachments/1470115973032968225/1529126641069064314/IMG_8873.png?ex=6a60cda9&is=6a5f7c29&hm=93fd23fbdfe467e1dfa42c7618076b5eacfbe9b63658adc2b9d3703ea629db52&)
- 📎 [IMG\_8874.png](https://cdn.discordapp.com/attachments/1470115973032968225/1529126641614327878/IMG_8874.png?ex=6a60cda9&is=6a5f7c29&hm=4f293476fd1150add5a6ffe532b9d35c8377babb29f92d64e2ff0f260380ef03&)
- 📎 [IMG\_8875.png](https://cdn.discordapp.com/attachments/1470115973032968225/1529126642130223204/IMG_8875.png?ex=6a60cda9&is=6a5f7c29&hm=5d51549a336dab4be2b77352c2d1a441cbc5202ba5cd056dbbe04bf2e5e20fa0&)
- 📎 [IMG\_8876.png](https://cdn.discordapp.com/attachments/1470115973032968225/1529126642872619162/IMG_8876.png?ex=6a60cda9&is=6a5f7c29&hm=a7a1c51c32c9ded2157c8c76f08427219bc0eb20f70ac650ecf60046feee1f79&)
- 📎 [IMG\_8877.png](https://cdn.discordapp.com/attachments/1470115973032968225/1529126643417747476/IMG_8877.png?ex=6a60cda9&is=6a5f7c29&hm=4978ecb9bf501e8dc8a6612821778735497a40d9d80e3ec364263305e321a227&)
- 📎 [IMG\_8878.png](https://cdn.discordapp.com/attachments/1470115973032968225/1529126644034437230/IMG_8878.png?ex=6a60cda9&is=6a5f7c29&hm=304791671beab2f24fb3c8ce51209e6bc9c5927ed847991f2f04168fff06e542&)
- 📎 [IMG\_8879.png](https://cdn.discordapp.com/attachments/1470115973032968225/1529126644621508770/IMG_8879.png?ex=6a60cda9&is=6a5f7c29&hm=584cef4123bf1d84bc9bba74744113f5063a0f6132483b682c30e29678c89aba&)
- 📎 [IMG\_8880.png](https://cdn.discordapp.com/attachments/1470115973032968225/1529126645179613215/IMG_8880.png?ex=6a60cdaa&is=6a5f7c2a&hm=e77afc29bb3faf38cbc6345690c89b6fe1b52f4fb075a7249f0689d0dad2897b&)
- 📎 [IMG\_8881.png](https://cdn.discordapp.com/attachments/1470115973032968225/1529126645674414121/IMG_8881.png?ex=6a60cdaa&is=6a5f7c2a&hm=8fa8a21df49fae2518129ad42675b766b801748b9d07ab59a9536b40df7dc452&)
- 📎 [IMG\_8882.png](https://cdn.discordapp.com/attachments/1470115973032968225/1529126646270132274/IMG_8882.png?ex=6a60cdaa&is=6a5f7c2a&hm=dc566d2c713b963ac07a7f8da34bd3da81f93cb6e9084953e5718fc33be1eb49&)
^msg-1529126646576320693

**Gurth Brooks** (`gurthbr0oks`) · 14:03:26 UTC
> Sim power
^msg-1529126664993374319

**Gurth Brooks** (`gurthbr0oks`) · 14:03:43 UTC
> 
- 📎 [IMG\_8863.png](https://cdn.discordapp.com/attachments/1470115973032968225/1529126729472544829/IMG_8863.png?ex=6a60cdbe&is=6a5f7c3e&hm=2306da2a80c0a4a1a6e09a9d45be221cb96945b1fe92082149f6ff4c1980636b&)
- 📎 [IMG\_8864.png](https://cdn.discordapp.com/attachments/1470115973032968225/1529126730017673426/IMG_8864.png?ex=6a60cdbe&is=6a5f7c3e&hm=7567b250f04906cd360cebb75d7dddfb1cbcaefba52ee1e686ed43f60be67d9e&)
- 📎 [IMG\_8865.png](https://cdn.discordapp.com/attachments/1470115973032968225/1529126730525180004/IMG_8865.png?ex=6a60cdbe&is=6a5f7c3e&hm=dd545aec955d5154e2713058abdf99ec175dd963640922c3df0cb7c2235fa02a&)
- 📎 [IMG\_8866.png](https://cdn.discordapp.com/attachments/1470115973032968225/1529126731359719475/IMG_8866.png?ex=6a60cdbe&is=6a5f7c3e&hm=f81d8315dcc79e8e78f14b127fb4c80cfae1470c04912e873b64c319b0c528b5&)
- 📎 [IMG\_8867.png](https://cdn.discordapp.com/attachments/1470115973032968225/1529126732169351258/IMG_8867.png?ex=6a60cdbe&is=6a5f7c3e&hm=594df832489703a05f34c525ab8808e57bebf04a7b2e837948d0e40e8c1ab11e&)
- 📎 [IMG\_8868.png](https://cdn.discordapp.com/attachments/1470115973032968225/1529126732848697386/IMG_8868.png?ex=6a60cdbe&is=6a5f7c3e&hm=beb3914a73686cba775f5c9065dfc04f21d9a0ea4cd1ee539e58053ae6c78085&)
- 📎 [IMG\_8869.png](https://cdn.discordapp.com/attachments/1470115973032968225/1529126733775769763/IMG_8869.png?ex=6a60cdbf&is=6a5f7c3f&hm=6e3e25f959c6db817f793d9a14e53ceda8e2af84ce7942b58235ce0c7ed9dd62&)
- 📎 [IMG\_8870.png](https://cdn.discordapp.com/attachments/1470115973032968225/1529126734396526723/IMG_8870.png?ex=6a60cdbf&is=6a5f7c3f&hm=d0d56d31f15956578e18f483ed8f134077327da5e179e1fb1e2642306a47dee3&)
- 📎 [IMG\_8871.png](https://cdn.discordapp.com/attachments/1470115973032968225/1529126734945845318/IMG_8871.png?ex=6a60cdbf&is=6a5f7c3f&hm=f6759d8b298b41ba9d96139ee63399c11101912763a9614ccbc685c67dffe4a4&)
- 📎 [IMG\_8872.png](https://cdn.discordapp.com/attachments/1470115973032968225/1529126735487172648/IMG_8872.png?ex=6a60cdbf&is=6a5f7c3f&hm=a2642a04c9e18b97cfba3a0a88457f5c253da246e0c341ad48c079e624689c6a&)
^msg-1529126735851950151

**Gurth Brooks** (`gurthbr0oks`) · 14:03:49 UTC
> Total power
^msg-1529126761772748870
