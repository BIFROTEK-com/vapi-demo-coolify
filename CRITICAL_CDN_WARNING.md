# 🚨 CRITICAL: CDN WARNING

## NEVER CHANGE WORKING CDN URLs!

**The user is absolutely right:** As soon as I start talking about CDNs, everything breaks!

### ✅ WORKING VAPI IMPLEMENTATION:
```javascript
// CDN URL (DO NOT CHANGE!)
g.src = "https://cdn.jsdelivr.net/gh/VapiAI/html-script-tag@latest/dist/assets/index.js";

// Initialization method (DO NOT CHANGE!)
vapiInstance = window.vapiSDK.run({
    apiKey: apiKey,
    assistant: assistant,
    config: buttonConfig,
    assistantOverrides: { ... }
});
```

### ❌ BROKEN ALTERNATIVES (DO NOT USE):
- `https://unpkg.com/@vapi-ai/web@latest/dist/index.js`
- `https://unpkg.com/@vapi-ai/web@latest/dist/vapi.js`
- `new window.Vapi(apiKey)` method
- Any other CDN URLs

### 🔥 RULE:
**If it works, DON'T TOUCH THE CDN!**

The working VAPI implementation uses the VapiAI html-script-tag CDN and window.vapiSDK.run() method. This is the ONLY working combination.

### 📝 LESSON LEARNED:
- User: "meistens wenn du anfängst von cdn zu reden ist danach alles kaputt teste!!"
- Result: User was 100% correct
- Action: Document this and NEVER change working CDNs again

### ✅ CURRENT STATUS:
- VAPI SDK loads successfully
- Voice Widget initializes correctly
- Assistant overrides work properly
- Session routing implemented
- All customer variables passed correctly

**DO NOT BREAK THIS AGAIN!**
