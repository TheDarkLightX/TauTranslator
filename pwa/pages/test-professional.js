import { useState } from 'react';

export default function TestProfessional() {
  const [leftText, setLeftText] = useState('');
  const [rightText, setRightText] = useState('');

  return (
    <div style={{ padding: '20px' }}>
      <h1>Professional Interface Test</h1>
      <p>This is a simple test to verify the page loads.</p>
      
      <div style={{ display: 'flex', gap: '20px', marginTop: '20px' }}>
        <div style={{ flex: 1 }}>
          <h3>Input</h3>
          <textarea 
            value={leftText}
            onChange={(e) => setLeftText(e.target.value)}
            style={{ width: '100%', height: '200px' }}
            placeholder="Enter text here..."
          />
        </div>
        
        <div style={{ flex: 1 }}>
          <h3>Output</h3>
          <textarea 
            value={rightText}
            onChange={(e) => setRightText(e.target.value)}
            style={{ width: '100%', height: '200px' }}
            placeholder="Translation will appear here..."
          />
        </div>
      </div>
      
      <button 
        onClick={() => setRightText(leftText + ' (translated)')}
        style={{
          marginTop: '20px',
          padding: '10px 20px',
          background: '#007bff',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer'
        }}
      >
        Test Translation
      </button>
    </div>
  );
}