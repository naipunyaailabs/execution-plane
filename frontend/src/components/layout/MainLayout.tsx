import { ReactNode, useState } from "react";
import { Sidebar } from "./Sidebar";
import { Button } from "@/components/ui/button";
import { ChevronLeft, ChevronRight } from "lucide-react";

interface MainLayoutProps {
  children: ReactNode;
}

export function MainLayout({ children }: MainLayoutProps) {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar isCollapsed={isSidebarCollapsed} />
      
      {/* Sleek Toggle Button */}
      <Button
        variant="outline"
        size="icon"
        className={`fixed top-4 z-50 h-8 w-8 rounded-full border-2 bg-background shadow-lg transition-all duration-300 hover:scale-110 ${
          isSidebarCollapsed ? 'left-4' : 'left-60'
        }`}
        onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
        title={isSidebarCollapsed ? "Expand sidebar" : "Collapse sidebar"}
      >
        {isSidebarCollapsed ? (
          <ChevronRight className="h-4 w-4" />
        ) : (
          <ChevronLeft className="h-4 w-4" />
        )}
      </Button>

      <main 
        className={`flex-1 overflow-y-auto bg-background transition-all duration-300 ${
          isSidebarCollapsed ? 'ml-0' : 'ml-64'
        }`}
      >
        <div className="min-h-screen">
          {children}
        </div>
      </main>
    </div>
  );
}
