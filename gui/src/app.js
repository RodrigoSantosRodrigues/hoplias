const { app, BrowserWindow, session } = require('electron');
const path = require('path');

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      webSecurity: true,
      //preload: path.join(__dirname, 'preload.js')
    },
    show: false,
    icon: path.join(__dirname, 'assets', 'icons', 'icon.png')
  });

  configureCache();

  mainWindow.loadURL('http://localhost:3003/user/login?client_mode=desktop'); // https://eloquent-monstera-5ebcf7.netlify.app
  
  mainWindow.webContents.on('did-finish-load', () => {
    mainWindow.show();
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

async function configureCache() {
  await session.defaultSession.clearCache();
  
  session.defaultSession.webRequest.onHeadersReceived((details, callback) => {
    const responseHeaders = details.responseHeaders || {};
    
    if (details.url.includes('/static/')) {
      responseHeaders['cache-control'] = ['public, max-age=31536000, immutable'];
    } else {
      responseHeaders['cache-control'] = ['public, max-age=3600'];
    }
    
    callback({ responseHeaders });
  });
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
});

module.exports = { createWindow, configureCache };
