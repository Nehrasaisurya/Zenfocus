const { app, BrowserWindow, ipcMain, Notification } = require("electron");
const path = require("path");
const fs = require("fs");
const { spawn } = require("child_process");

process.on("unhandledRejection", (reason, promise) => {
  console.error("Unhandled Rejection at:", promise, "reason:", reason);
});

const isDev = process.env.NODE_ENV === "development" || !app.isPackaged;

if (isDev) {
  require("electron-reload")(__dirname, {
    electron: path.join(__dirname, "node_modules", ".bin", "electron"),
    hardResetMethod: "exit",
  });
}

let pythonProcess;
let win;

const showBreakNotification = () => {
  const notification = new Notification({
    title: "Take a Break Reminder",
    body: "You've been working for a long time. It's time to take a break.",
    actions: [
      { type: "button", text: "Ignore" },
      { type: "button", text: "Take Break" },
    ],
    closeButtonText: "Dismiss",
  });

  notification.show();

  notification.on("action", (event, index) => {
    if (index === 0) {
      console.log("Ignore button clicked");
    } else if (index === 1) {
      console.log("Take Break button clicked");
      win.webContents.send("reset-timer"); 
    }
  });

  notification.on("click", () => {
   
    const gameFilePath = path.join(__dirname, "public/Game.html");
    win.loadFile(gameFilePath);
  });

  notification.on("close", () => {
    console.log("Notification dismissed");
  });
};

const startBreakNotificationTimer = () => {
  setInterval(showBreakNotification, 60000); 
};

function createWindow() {
  win = new BrowserWindow({
    width: 800,
    height: 600,
    frame: true,
    fullscreenable: true,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      nodeIntegration: false, 
      contextIsolation: true, 
    },
  });

  
  if (isDev) {
    win.loadURL("http://localhost:3000");
    win.webContents.openDevTools();
  } else {
    win.loadFile(path.join(__dirname, "public/index.html"));
  }

  win.maximize();
  win.setFullScreenable(true);

  if (!isDev) {
    win.setMenu(null);
  }
}

app.whenReady().then(() => {
  createWindow();

  startBreakNotificationTimer();

  pythonProcess = spawn("python", [path.join(__dirname, "main.py")], {
    windowsHide: true,
    detached: true, 
    stdio: "ignore", 
  });
  pythonProcess.unref();

  pythonProcess.on("error", (err) => {
    console.error("Failed to start Python process:", err);
  });

  pythonProcess.on("close", (code) => {
    console.log(`Python process exited with code ${code}`);
  });

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
  if (pythonProcess) {
    pythonProcess.kill();
  }
});

const usageFilePath = path.join(__dirname, "usage_log.json");


ipcMain.handle("get-app-usage", async () => {
  return new Promise((resolve, reject) => {
    fs.readFile(usageFilePath, "utf8", (err, data) => {
      if (err) {
        console.error("Error reading usage_log.json file:", err);
        return reject("Error reading usage log");
      }
      try {
        const jsonData = JSON.parse(data);
        resolve(jsonData); 
      } catch (parseError) {
        console.error("Error parsing usage_log.json:", parseError);
        return reject("Error parsing usage log");
      }
    });
  });
});


ipcMain.on("save-onboarding-data", (event, data) => {
  const onboardingFilePath = path.join(__dirname, "onboardingData.json");

  fs.writeFile(onboardingFilePath, JSON.stringify(data, null, 2), (err) => {
    if (err) {
      console.error("Error saving onboarding data:", err);
      event.reply("onboarding-data-saved", {
        success: false,
        message: "Failed to save data",
      });
      return;
    }
    console.log("Onboarding data saved successfully");
    event.reply("onboarding-data-saved", {
      success: true,
      message: "Data saved successfully",
    });
  });
});


ipcMain.handle("show-break-notification", showBreakNotification);
