import { Card } from "@/components/ui/card";
import { Bot, GitBranch, Repeat, Play, Square, Settings, AlertCircle, MessageSquare, Monitor } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";

interface NodeTypeConfig {
  type: string;
  label: string;
  icon: React.ElementType;
  description: string;
  color: string;
  bgColor: string;
}

const nodeTypeConfigs: NodeTypeConfig[] = [
  {
    type: "startNode",
    label: "Start",
    icon: Play,
    description: "Entry point of the workflow",
    color: "text-green-600",
    bgColor: "bg-green-50 hover:bg-green-100 border-green-300",
  },
  {
    type: "endNode",
    label: "End",
    icon: Square,
    description: "Exit point of the workflow",
    color: "text-red-600",
    bgColor: "bg-red-50 hover:bg-red-100 border-red-300",
  },
  {
    type: "agentNode",
    label: "Agent",
    icon: Bot,
    description: "Execute an AI agent",
    color: "text-blue-600",
    bgColor: "bg-blue-50 hover:bg-blue-100 border-blue-300",
  },
  {
    type: "conditionNode",
    label: "Condition",
    icon: GitBranch,
    description: "Branch based on a condition",
    color: "text-yellow-600",
    bgColor: "bg-yellow-50 hover:bg-yellow-100 border-yellow-300",
  },
  {
    type: "loopNode",
    label: "Loop",
    icon: Repeat,
    description: "Repeat actions multiple times",
    color: "text-purple-600",
    bgColor: "bg-purple-50 hover:bg-purple-100 border-purple-300",
  },
  {
    type: "actionNode",
    label: "Action",
    icon: Settings,
    description: "Execute a custom action",
    color: "text-indigo-600",
    bgColor: "bg-indigo-50 hover:bg-indigo-100 border-indigo-300",
  },
  {
    type: "errorHandlerNode",
    label: "Error Handler",
    icon: AlertCircle,
    description: "Handle errors and exceptions",
    color: "text-orange-600",
    bgColor: "bg-orange-50 hover:bg-orange-100 border-orange-300",
  },
  {
    type: "chatNode",
    label: "Chat / Manual",
    icon: MessageSquare,
    description: "Manual trigger with chat interface",
    color: "text-cyan-600",
    bgColor: "bg-cyan-50 hover:bg-cyan-100 border-cyan-300",
  },
  {
    type: "displayNode",
    label: "Display Output",
    icon: Monitor,
    description: "Display and preview data beautifully",
    color: "text-emerald-600",
    bgColor: "bg-emerald-50 hover:bg-emerald-100 border-emerald-300",
  },
];

export function NodePalette() {
  const onDragStart = (event: React.DragEvent, nodeType: string) => {
    event.dataTransfer.setData("application/reactflow", nodeType);
    event.dataTransfer.effectAllowed = "move";
  };

  return (
    <Card className="w-64 h-full flex flex-col overflow-hidden">
      <div className="p-4 border-b flex-shrink-0">
        <h3 className="font-semibold text-lg">Node Palette</h3>
        <p className="text-xs text-muted-foreground mt-1">
          Drag and drop nodes to the canvas
        </p>
      </div>
      
      <ScrollArea className="flex-1 overflow-auto">
        <div className="space-y-2 p-3">
          {nodeTypeConfigs.map((config) => {
            const Icon = config.icon;
            return (
              <div
                key={config.type}
                className={`p-3 rounded-lg border-2 cursor-move transition-all ${config.bgColor} dark:bg-gray-800 dark:border-gray-600`}
                draggable
                onDragStart={(e) => onDragStart(e, config.type)}
              >
                <div className="flex items-start gap-3">
                  <div className={`p-2 rounded-md ${config.color} bg-white dark:bg-gray-700`}>
                    <Icon className="w-5 h-5" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="font-semibold text-sm">{config.label}</div>
                    <div className="text-xs text-muted-foreground mt-1">
                      {config.description}
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </ScrollArea>
      
      <div className="p-3 border-t bg-muted/50">
        <p className="text-xs text-muted-foreground text-center">
          💡 Tip: Connect nodes by dragging from output to input
        </p>
      </div>
    </Card>
  );
}
