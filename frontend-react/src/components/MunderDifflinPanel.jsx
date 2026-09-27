import React from 'react';
import MunderDifflin from '../pages/MunderDifflin/MunderDifflin';

export default function MunderDifflinPanel() {
  return (
    <div
      id="munder-panel"
      role="tabpanel"
      aria-labelledby="munder-tab"
      tabIndex={0}
      className="w-full h-full bg-[#f7f3eb]"
    >
      <MunderDifflin />
    </div>
  );
}
