import { useState } from "react";
import { WorkflowList } from "@/components/workflow/WorkflowList";
import { WorkflowBuilder } from "@/components/workflow/WorkflowBuilder";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Sparkles } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { Link } from "react-router-dom";

export default function Workflows() {
  const [view, setView] = useState<"list" | "builder">("list");
  const navigate = useNavigate();

  return (
    <div className="container py-8">
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-4">
          <Button 
            variant="ghost" 
            size="icon" 
            onClick={() => navigate("/")}
            className="h-8 w-8"
          >
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <h1 className="text-3xl font-bold tracking-tight">Workflows</h1>
        </div>
        {view === "list" && (
          <div className="flex gap-2">
            <Button variant="outline" asChild>
              <Link to="/workflow-builder">
                <Sparkles className="w-4 h-4 mr-2" />
                Simple Builder
              </Link>
            </Button>
            <Button asChild>
              <Link to="/production-workflow">
                Production Builder
              </Link>
            </Button>
          </div>
        )}
        {view === "builder" && (
          <Button variant="outline" onClick={() => setView("list")}>
            Cancel
          </Button>
        )}
      </div>

      {view === "list" && <WorkflowList />}
      {view === "builder" && <WorkflowBuilder />}
    </div>
  );
}