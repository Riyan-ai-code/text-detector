import { useState } from "react";
import Sidebar from "./components/Sidebar";
import Dashboard from "./pages/Dashboard";

function App() {
  const [selectedModel, setSelectedModel] = useState("all");
  const [darkMode, setDarkMode] = useState(true);

  return (
    <div className={`app-container ${darkMode ? "dark-theme" : "light-theme"}`}>
      <Sidebar selectedModel={selectedModel} setSelectedModel={setSelectedModel} />
      <Dashboard
        selectedModel={selectedModel}
        setSelectedModel={setSelectedModel}
        darkMode={darkMode}
        setDarkMode={setDarkMode}
      />
    </div>
  );
}

export default App;