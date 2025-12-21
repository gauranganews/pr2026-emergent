import { useState } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import AstroPrediction from "@/components/AstroPrediction";

function App() {
  return (
    <div className="App dark">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<AstroPrediction />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;