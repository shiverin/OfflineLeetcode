const { app, BrowserWindow } = require("electron");
const { spawn } = require("child_process");
const path = require("path");

let backend;

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      contextIsolation: true
    }
  });

  if (process.env.NODE_ENV === "development") {
    win.loadURL("http://localhost:5173");
  } else {
    const frontendPath = path.join(
      __dirname,
      "../../offline-leetcode/dist/index.html"
    );

    console.log("Loading frontend from:", frontendPath);
    win.loadFile(frontendPath);
      }
}

app.whenReady().then(() => {
  backend = spawn("python3", ["app.py"], {
    cwd: path.join(__dirname, "../../backend")
  });

  backend.stdout.on("data", d => console.log(d.toString()));
  backend.stderr.on("data", d => console.error(d.toString()));

  createWindow();
});
