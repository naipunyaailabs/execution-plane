import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Trash2, Bot, RefreshCw } from "lucide-react";
import { toast } from "@/hooks/use-toast";

interface Agent {
  agent_id: string;
  name: string;
  agent_type: string;
  llm_provider: string;
  llm_model: string;
  temperature: number;
  system_prompt: string;
  tools: string[];
  max_iterations: number;
  memory_type: string;
  streaming_enabled: boolean;
  human_in_loop: boolean;
  recursion_limit: number;
  created_at: string;
  updated_at: string;
}

interface AgentListProps {
  onAgentDeleted?: () => void;
}

export function AgentList({ onAgentDeleted }: AgentListProps) {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchAgents();
  }, []);

  const fetchAgents = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/v1/agents');
      if (response.ok) {
        const data = await response.json();
        setAgents(data);
      }
    } catch (error) {
      console.error("Error fetching agents:", error);
      toast({
        title: "Error",
        description: "Failed to load agents",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleDeleteAgent = async (agentId: string, agentName: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/agents/${agentId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        // Remove the agent from the local state
        setAgents(agents.filter(agent => agent.agent_id !== agentId));
        toast({
          title: "Agent Deleted",
          description: `${agentName} has been successfully deleted.`,
        });
        // Call the callback if provided
        if (onAgentDeleted) {
          onAgentDeleted();
        }
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to delete agent');
      }
    } catch (error) {
      console.error("Error deleting agent:", error);
      toast({
        title: "Error Deleting Agent",
        description: error.message || "Failed to delete agent. Please try again.",
        variant: "destructive",
      });
    }
  };

  const handleRefresh = () => {
    setRefreshing(true);
    fetchAgents();
  };

  if (loading && !refreshing) {
    return (
      <div className="flex justify-center items-center h-32">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Your Agents</h2>
        <Button
          variant="ghost"
          size="sm"
          onClick={handleRefresh}
          disabled={refreshing}
        >
          <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
        </Button>
      </div>
      {agents.length === 0 ? (
        <Card className="p-6 text-center">
          <p className="text-muted-foreground">No agents created yet. Create your first agent above!</p>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {agents.map((agent) => (
            <Card key={agent.agent_id} className="p-4 flex flex-col">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center">
                    <Bot className="w-4 h-4 text-primary-foreground" />
                  </div>
                  <div>
                    <h3 className="font-medium">{agent.name}</h3>
                    <p className="text-xs text-muted-foreground capitalize">{agent.agent_type}</p>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => handleDeleteAgent(agent.agent_id, agent.name)}
                  className="text-destructive hover:text-destructive hover:bg-destructive/10"
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
              <div className="mt-3 text-xs text-muted-foreground">
                <p className="truncate">{agent.llm_provider} - {agent.llm_model}</p>
                <p className="truncate mt-1">Tools: {agent.tools.length > 0 ? agent.tools.join(", ") : "None"}</p>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}