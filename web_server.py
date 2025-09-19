#!/usr/bin/env python3
"""
CrewAI Flow Control Center Web Server
FastAPI server for managing and executing CrewAI flows
"""

import os
import sys
import json
import asyncio
import logging
import concurrent.futures
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FlowExecutionRequest(BaseModel):
    flow_name: str
    topic: str = "Latest AI and Tech Skills Trends"


class FlowStatus(BaseModel):
    flow_name: str
    status: str
    created_at: str
    output_file: Optional[str] = None


class FlowPlot(BaseModel):
    flow_name: str
    plot_file: str
    created_at: str


class FlowControlServer:
    def __init__(self):
        self.app = FastAPI(
            title="CrewAI Flow Control Center",
            description="Web interface for managing CrewAI flows",
            version="1.0.0"
        )
        self.setup_middleware()
        self.setup_routes()
        self.setup_static_files()
        
        # Flow execution tracking
        self.active_flows: Dict[str, asyncio.Task] = {}
        self.flow_history: List[FlowStatus] = []

    def setup_middleware(self):
        """Setup CORS and other middleware"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def setup_static_files(self):
        """Setup static file serving"""
        # Serve the web interface
        self.app.mount("/assets", StaticFiles(directory="www/assets"), name="assets")
        self.app.mount("/plots", StaticFiles(directory="www/plots"), name="plots")

    def setup_routes(self):
        """Setup API routes"""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def serve_index():
            """Serve the main web interface"""
            try:
                with open("www/index.html", "r", encoding="utf-8") as f:
                    return HTMLResponse(content=f.read())
            except FileNotFoundError:
                raise HTTPException(status_code=404, detail="Web interface not found")

        @self.app.get("/api/flows")
        async def list_flows():
            """List available flows"""
            flows = [
                {
                    "name": "create_new_post_flow",
                    "display_name": "Create New Post Flow",
                    "description": "Generate social media posts using multi-agent collaboration",
                    "agents": ["Coach", "Influencer", "Critic"],
                    "status": "active",
                    "runs": len([f for f in self.flow_history if f.flow_name == "create_new_post_flow"]),
                    "avg_runtime": "2.1s"
                }
            ]
            return {"flows": flows}

        @self.app.get("/api/flow-plots")
        async def list_flow_plots():
            """List available flow plot files"""
            plots_dir = Path("www/plots")
            plots = []
            
            if plots_dir.exists():
                for plot_file in plots_dir.glob("*.html"):
                    flow_name = plot_file.stem.replace("_plot", "")
                    stat = plot_file.stat()
                    plots.append(FlowPlot(
                        flow_name=flow_name,
                        plot_file=str(plot_file.name),
                        created_at=datetime.fromtimestamp(stat.st_mtime).isoformat()
                    ))
            
            return {"plots": plots}

        @self.app.post("/api/execute-flow")
        async def execute_flow(request: FlowExecutionRequest):
            """Execute a CrewAI flow with streaming output"""
            
            async def flow_stream():
                flow_id = f"{request.flow_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                try:
                    # Send initial status
                    yield f"data: {json.dumps({'type': 'log', 'message': '🚀 Starting Flow Execution', 'level': 'info'})}\n\n"
                    yield f"data: {json.dumps({'type': 'log', 'message': f'📋 Flow: {request.flow_name}', 'level': 'info'})}\n\n"
                    yield f"data: {json.dumps({'type': 'log', 'message': f'📝 Topic: {request.topic}', 'level': 'info'})}\n\n"
                    
                    # Import and execute the flow
                    if request.flow_name == "create_new_post_flow":
                        yield f"data: {json.dumps({'type': 'progress', 'step': 'Import', 'message': 'Loading flow module'})}\n\n"
                        
                        try:
                            yield f"data: {json.dumps({'type': 'log', 'message': 'Attempting import...', 'level': 'debug'})}\n\n"
                            from src.linkedin.flows.create_new_post_flow import run_create_new_post_flow
                            yield f"data: {json.dumps({'type': 'log', 'message': 'Import successful', 'level': 'debug'})}\n\n"
                            
                            yield f"data: {json.dumps({'type': 'progress', 'step': 'Initialize', 'message': 'Setting up flow state'})}\n\n"
                            
                            # Execute the flow in a thread pool to handle CrewAI's internal asyncio.run()
                            yield f"data: {json.dumps({'type': 'log', 'message': 'Starting flow in thread pool...', 'level': 'debug'})}\n\n"
                            
                            def run_flow_sync():
                                """Wrapper to run the CrewAI flow in a separate thread"""
                                try:
                                    return run_create_new_post_flow(request.topic)
                                except Exception as e:
                                    print(f"Flow execution error: {e}")
                                    raise
                            
                            try:
                                # Use thread pool executor to run the CrewAI flow
                                loop = asyncio.get_event_loop()
                                with concurrent.futures.ThreadPoolExecutor() as executor:
                                    result = await loop.run_in_executor(executor, run_flow_sync)
                                
                                yield f"data: {json.dumps({'type': 'log', 'message': f'Flow execution completed. Result: {type(result)}', 'level': 'debug'})}\n\n"
                                
                                yield f"data: {json.dumps({'type': 'progress', 'step': 'Generate', 'message': 'Running multi-agent collaboration'})}\n\n"
                                yield f"data: {json.dumps({'type': 'progress', 'step': 'Save', 'message': 'Saving output and generating plot'})}\n\n"
                                
                                # Find the output file
                                output_dir = Path("output/posts")
                                output_files = list(output_dir.glob(f"*{request.topic.replace(' ', '_')}*.txt"))
                                output_file = str(output_files[-1]) if output_files else "output/posts/latest.txt"
                                
                                # Record successful execution
                                self.flow_history.append(FlowStatus(
                                    flow_name=request.flow_name,
                                    status="completed",
                                    created_at=datetime.now().isoformat(),
                                    output_file=output_file
                                ))
                                
                                yield f"data: {json.dumps({'type': 'success', 'message': 'Flow completed successfully!', 'output_file': output_file})}\n\n"
                                
                            except Exception as flow_error:
                                error_msg = f"Flow execution error: {str(flow_error)}"
                                yield f"data: {json.dumps({'type': 'error', 'message': error_msg})}\n\n"
                                logger.error(f"Flow execution failed: {flow_error}")
                                import traceback
                                logger.error(traceback.format_exc())
                            
                        except ImportError as e:
                            error_msg = f"Failed to import flow module: {str(e)}"
                            yield f"data: {json.dumps({'type': 'error', 'message': error_msg})}\n\n"
                            
                        except Exception as e:
                            error_msg = f"Flow execution failed: {str(e)}"
                            yield f"data: {json.dumps({'type': 'error', 'message': error_msg})}\n\n"
                            
                            # Record failed execution
                            self.flow_history.append(FlowStatus(
                                flow_name=request.flow_name,
                                status="failed",
                                created_at=datetime.now().isoformat()
                            ))
                    else:
                        yield f"data: {json.dumps({'type': 'error', 'message': f'Unknown flow: {request.flow_name}'})}\n\n"
                
                except Exception as e:
                    logger.error(f"Flow execution error: {e}")
                    yield f"data: {json.dumps({'type': 'error', 'message': f'Unexpected error: {str(e)}'})}\n\n"

            return StreamingResponse(
                flow_stream(),
                media_type="text/plain",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Content-Type": "text/event-stream",
                }
            )

        @self.app.get("/api/flow-history")
        async def get_flow_history():
            """Get flow execution history"""
            return {"history": self.flow_history}

        @self.app.get("/api/stats")
        async def get_stats():
            """Get dashboard statistics"""
            total_runs = len(self.flow_history)
            successful_runs = len([f for f in self.flow_history if f.status == "completed"])
            success_rate = (successful_runs / total_runs * 100) if total_runs > 0 else 0
            
            return {
                "total_runs": total_runs,
                "successful_runs": successful_runs,
                "success_rate": f"{success_rate:.1f}%",
                "active_flows": len(self.active_flows),
                "avg_runtime": "2.1s"  # This would be calculated from actual runtimes
            }

        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {"status": "healthy", "timestamp": datetime.now().isoformat()}

    def run(self, host: str = "localhost", port: int = 8000, reload: bool = False):
        """Run the web server"""
        logger.info(f"Starting CrewAI Flow Control Center on http://{host}:{port}")
        logger.info("Web interface available at: http://localhost:8000")
        
        uvicorn.run(
            "web_server:server.app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )


# Create global server instance
server = FlowControlServer()

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="CrewAI Flow Control Center")
    parser.add_argument("--host", default="localhost", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    
    args = parser.parse_args()
    
    # Ensure required directories exist
    os.makedirs("www/plots", exist_ok=True)
    os.makedirs("output/posts", exist_ok=True)
    
    server.run(host=args.host, port=args.port, reload=args.reload)

if __name__ == "__main__":
    main()