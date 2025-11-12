import React, { useState } from 'react';
import './App.css';
import LayoutParser from './components/LayoutParser';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>📰 Newspaper Layout Parser</h1>
        <p>Upload a newspaper image to analyze its layout structure</p>
      </header>
      <main>
        <LayoutParser />
      </main>
    </div>
  );
}

export default App;

