'use client';

import { useState } from 'react';

interface ExampleEntryProps {
  title?: string;
}

export default function ExampleEntry({ title = 'Example Slice' }: ExampleEntryProps) {
  const [clicks, setClicks] = useState(0);

  return (
    <article style={{ border: '1px solid #334155', padding: '1rem', borderRadius: '0.5rem', marginTop: '1.5rem' }}>
      <header>
        <h2>{title}</h2>
        <p>This placeholder shows where slice-specific UI would mount.</p>
      </header>
      <button
        type="button"
        onClick={() => setClicks((count) => count + 1)}
        style={{
          marginTop: '0.75rem',
          padding: '0.5rem 0.75rem',
          background: '#2563eb',
          color: '#f8fafc',
          border: 'none',
          borderRadius: '0.375rem'
        }}
      >
        Interact ({clicks})
      </button>
    </article>
  );
}
