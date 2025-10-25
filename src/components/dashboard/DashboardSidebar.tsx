"use client";

import { useState } from "react";
import {
  Home,
  MessageSquare,
  Users,
  Edit,
  Settings,
  BarChart3,
  Star,
  Lock,
  ChevronLeft,
  ChevronRight,
  Bot,
  Globe,
  TrendingUp,
  Activity
} from "lucide-react";

interface DashboardSidebarProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
}

const sidebarItems = [
  {
    id: "dashboard",
    label: "Dashboard",
    icon: Home,
    description: "Performance overview"
  },
  {
    id: "conversations-log",
    label: "Conversations Log",
    icon: MessageSquare,
    description: "Monitoring, Audit Log"
  },
  {
    id: "agent-management",
    label: "Agent Management",
    icon: Users,
    description: "Handoff/Human Agent Control"
  },
  {
    id: "intents-training",
    label: "Intents & Training",
    icon: Edit,
    description: "Editing Intents, Continuous Learning"
  },
  {
    id: "system-settings",
    label: "System Settings",
    icon: Settings,
    description: "API, Security, Rules"
  },
  {
    id: "analytics-reports",
    label: "Analytics & Reports",
    icon: BarChart3,
    description: "Viewing performance data"
  },
  {
    id: "review-ratings",
    label: "Review & Ratings",
    icon: Star,
    description: "Customer Satisfaction Monitoring"
  },
  {
    id: "security-logs",
    label: "Security & Logs",
    icon: Lock,
    description: "PII Masking, Compliance Audits"
  }
];

export default function DashboardSidebar({ activeTab, onTabChange, isCollapsed, onToggleCollapse }: DashboardSidebarProps) {
  return (
    <div className={`${isCollapsed ? 'w-16' : 'w-64'} bg-slate-900 text-white h-screen fixed left-0 top-16 transition-all duration-300 z-40 flex flex-col`}>
      {/* Header */}
      <div className="p-4 border-b border-slate-700 flex items-center justify-between">
        {!isCollapsed && (
          <div>
            <h2 className="text-lg font-semibold text-white">Navigation</h2>
            <p className="text-xs text-slate-400">Platform Management</p>
          </div>
        )}
        <button
          onClick={onToggleCollapse}
          className="p-2 rounded-lg hover:bg-slate-800 transition-colors"
          title={isCollapsed ? "Expand Sidebar" : "Collapse Sidebar"}
        >
          {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
      </div>

      {/* Navigation Items */}
      <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
        {sidebarItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;

          return (
            <button
              key={item.id}
              onClick={() => onTabChange(item.id)}
              className={`w-full flex items-center gap-3 px-3 py-3 rounded-lg transition-all duration-200 group ${
                isActive
                  ? 'bg-blue-600 text-white shadow-lg'
                  : 'text-slate-300 hover:bg-slate-800 hover:text-white'
              }`}
              title={isCollapsed ? item.label : undefined}
            >
              <Icon className={`w-5 h-5 flex-shrink-0 ${isActive ? 'text-white' : 'text-slate-400 group-hover:text-white'}`} />
              {!isCollapsed && (
                <div className="flex-1 text-left">
                  <div className="font-medium text-sm">{item.label}</div>
                  <div className="text-xs text-slate-500 mt-0.5">{item.description}</div>
                </div>
              )}
            </button>
          );
        })}
      </nav>

      {/* Footer */}
      {!isCollapsed && (
        <div className="p-4 border-t border-slate-700">
          <div className="bg-slate-800 rounded-lg p-3">
            <div className="flex items-center gap-2 mb-2">
              <Activity className="w-4 h-4 text-green-400" />
              <span className="text-xs font-medium text-green-400">System Status</span>
            </div>
            <p className="text-xs text-slate-400">All systems operational</p>
          </div>
        </div>
      )}
    </div>
  );
}
