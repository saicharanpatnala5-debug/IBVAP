import React from 'react';
import { SeverityLevel } from '../../types';
import { getSeverityBadgeStyles } from '../../utils/formatters';

interface AlertBadgeProps {
  severity: SeverityLevel;
}

export const AlertBadge: React.FC<AlertBadgeProps> = ({ severity }) => {
  const styles = getSeverityBadgeStyles(severity);

  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase tracking-wider border ${styles.bg} ${styles.text} ${styles.border} ${styles.glow}`}
    >
      {severity}
    </span>
  );
};
