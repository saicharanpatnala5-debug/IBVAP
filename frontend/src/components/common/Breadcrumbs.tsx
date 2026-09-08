import React from 'react';
import { ChevronRight, Home } from 'lucide-react';

interface BreadcrumbItem {
  label: string;
  onClick?: () => void;
  isCurrent?: boolean;
}

interface BreadcrumbsProps {
  items: BreadcrumbItem[];
}

export const Breadcrumbs: React.FC<BreadcrumbsProps> = ({ items }) => {
  return (
    <nav className="flex items-center space-x-2 text-xs font-mono text-slate-400 mb-4" aria-label="Breadcrumb">
      <button 
        onClick={items[0]?.onClick}
        className="flex items-center space-x-1 hover:text-emerald-400 transition-colors focus:outline-none"
      >
        <Home className="w-3.5 h-3.5" />
        <span>HQ</span>
      </button>

      {items.map((item, index) => (
        <div key={index} className="flex items-center space-x-2 group">
          <ChevronRight className="w-3 h-3 text-slate-600 group-hover:translate-x-0.5 transition-transform duration-200" />
          {item.isCurrent ? (
            <span className="text-emerald-400 font-semibold">{item.label}</span>
          ) : (
            <button
              onClick={item.onClick}
              className="hover:text-slate-200 transition-colors focus:outline-none"
            >
              {item.label}
            </button>
          )}
        </div>
      ))}
    </nav>
  );
};
