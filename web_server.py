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
    experience_text: Optional[str] = None  # For experience blog flow


class FlowStatus(BaseModel):
    flow_name: str
    status: str
    created_at: str
    output_file: Optional[str] = None


class FlowPlot(BaseModel):
    flow_name: str
    plot_file: str
    created_at: str


class KnowledgeResetRequest(BaseModel):
    type: str = "topics"  # topics, web, or all


class TopicCheckRequest(BaseModel):
    topic: str


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
                    "agents": ["Coach", "Influencer", "Researcher"],
                    "status": "active",
                    "runs": len([f for f in self.flow_history if f.flow_name == "create_new_post_flow"]),
                    "avg_runtime": "2.1s"
                },
                {
                    "name": "create_blog_from_experience_flow",
                    "display_name": "Create Blog From Experience Flow",
                    "description": "Transform personal experiences into comprehensive blog posts",
                    "agents": ["Coach", "Researcher", "Writer"],
                    "status": "active",
                    "runs": len([f for f in self.flow_history if f.flow_name == "create_blog_from_experience_flow"]),
                    "avg_runtime": "3.2s"
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
                            import sys
                            import os
                            sys.path.insert(0, os.path.join(os.getcwd(), 'flows', 'linkedin_content_flow', 'src'))
                            from linkedin_content_flow.main import LinkedInContentFlow
                            yield f"data: {json.dumps({'type': 'log', 'message': 'Import successful', 'level': 'debug'})}\n\n"
                            
                            yield f"data: {json.dumps({'type': 'progress', 'step': 'Initialize', 'message': 'Setting up flow state'})}\n\n"
                            
                            # Execute the flow in a thread pool to handle CrewAI's internal asyncio.run()
                            yield f"data: {json.dumps({'type': 'log', 'message': 'Starting flow in thread pool...', 'level': 'debug'})}\n\n"
                            
                            def run_flow_sync():
                                """Wrapper to run the CrewAI flow in a separate thread"""
                                try:
                                    flow = LinkedInContentFlow()
                                    return flow.kickoff(inputs={"topic": request.topic})
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
                                output_files = list(output_dir.glob(f"*{request.topic.replace(' ', '_')}*.md"))
                                output_file = str(output_files[-1]) if output_files else "output/posts/latest.md"
                                
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
                            
                    elif request.flow_name == "create_blog_from_experience_flow":
                        # Handle experience blog flow
                        if not request.experience_text:
                            yield f"data: {json.dumps({'type': 'error', 'message': 'Experience text is required for this flow'})}\n\n"
                            return
                            
                        yield f"data: {json.dumps({'type': 'progress', 'step': 'Import', 'message': 'Loading experience blog flow module'})}\n\n"
                        
                        try:
                            yield f"data: {json.dumps({'type': 'log', 'message': 'Attempting import...', 'level': 'debug'})}\n\n"
                            import sys
                            import os
                            sys.path.insert(0, os.path.join(os.getcwd(), 'flows', 'experience_blog_flow', 'src'))
                            from experience_blog_flow.main import ExperienceBlogFlow
                            yield f"data: {json.dumps({'type': 'log', 'message': 'Import successful', 'level': 'debug'})}\n\n"
                            
                            yield f"data: {json.dumps({'type': 'progress', 'step': 'Initialize', 'message': 'Setting up experience blog flow state'})}\n\n"
                            
                            # Execute the flow in a thread pool to handle CrewAI's internal asyncio.run()
                            yield f"data: {json.dumps({'type': 'log', 'message': 'Starting experience blog flow in thread pool...', 'level': 'debug'})}\n\n"
                            
                            def run_experience_flow_sync():
                                """Wrapper to run the CrewAI experience blog flow in a separate thread"""
                                try:
                                    flow = ExperienceBlogFlow()
                                    return flow.kickoff(inputs={"experience_text": request.experience_text})
                                except Exception as e:
                                    print(f"Experience blog flow execution error: {e}")
                                    raise
                            
                            try:
                                # Use thread pool executor to run the CrewAI flow
                                loop = asyncio.get_event_loop()
                                with concurrent.futures.ThreadPoolExecutor() as executor:
                                    result = await loop.run_in_executor(executor, run_experience_flow_sync)
                                
                                yield f"data: {json.dumps({'type': 'log', 'message': f'Experience blog flow execution completed. Result: {type(result)}', 'level': 'debug'})}\n\n"
                                
                                yield f"data: {json.dumps({'type': 'progress', 'step': 'Analyze', 'message': 'Analyzing personal experience'})}\n\n"
                                yield f"data: {json.dumps({'type': 'progress', 'step': 'Research', 'message': 'Conducting enhanced research'})}\n\n"
                                yield f"data: {json.dumps({'type': 'progress', 'step': 'Generate', 'message': 'Creating comprehensive blog post'})}\n\n"
                                yield f"data: {json.dumps({'type': 'progress', 'step': 'Save', 'message': 'Saving enhanced blog content'})}\n\n"
                                
                                # Find the output file
                                output_dir = Path("output/blogs")
                                output_files = list(output_dir.glob(f"blog_post_*.md"))
                                output_file = str(output_files[-1]) if output_files else "output/blogs/latest.md"
                                
                                # Record successful execution
                                self.flow_history.append(FlowStatus(
                                    flow_name=request.flow_name,
                                    status="completed",
                                    created_at=datetime.now().isoformat(),
                                    output_file=output_file
                                ))
                                
                                yield f"data: {json.dumps({'type': 'success', 'message': 'Experience blog flow completed successfully!', 'output_file': output_file})}\n\n"
                                
                            except Exception as flow_error:
                                error_msg = f"Experience blog flow execution error: {str(flow_error)}"
                                yield f"data: {json.dumps({'type': 'error', 'message': error_msg})}\n\n"
                                logger.error(f"Experience blog flow execution failed: {flow_error}")
                                import traceback
                                logger.error(traceback.format_exc())
                            
                        except ImportError as e:
                            error_msg = f"Failed to import experience blog flow module: {str(e)}"
                            yield f"data: {json.dumps({'type': 'error', 'message': error_msg})}\n\n"
                            
                        except Exception as e:
                            error_msg = f"Experience blog flow execution failed: {str(e)}"
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

        @self.app.get("/api/knowledge/stats")
        async def get_knowledge_stats():
            """Get knowledge statistics"""
            try:
                from helpers.knowledge_helper import KnowledgeHelper
                helper = KnowledgeHelper()
                stats = helper.get_knowledge_stats()
                return {"success": True, "data": stats}
            except Exception as e:
                logger.error(f"Error getting knowledge stats: {e}")
                return {"success": False, "error": str(e)}

        @self.app.post("/api/knowledge/reset")
        async def reset_knowledge(request: KnowledgeResetRequest):
            """Reset knowledge data"""
            try:
                from helpers.knowledge_helper import KnowledgeHelper
                helper = KnowledgeHelper()
                
                if request.type == "topics":
                    success = helper.reset_article_memory()
                    message = "Topic checking (article memory) reset successfully"
                elif request.type == "web":
                    success = helper.reset_web_search_results()
                    message = "Web search results reset successfully"
                elif request.type == "all":
                    success = helper.reset_all_knowledge()
                    message = "All knowledge data reset successfully"
                else:
                    return {"success": False, "error": "Invalid reset type"}
                
                return {
                    "success": success,
                    "message": message if success else "Reset operation failed"
                }
            except Exception as e:
                logger.error(f"Error resetting knowledge: {e}")
                return {"success": False, "error": str(e)}

        @self.app.post("/api/knowledge/check-topic")
        async def check_topic_coverage(request: TopicCheckRequest):
            """Check if a topic has been covered before"""
            try:
                from helpers.knowledge_helper import check_topic_similarity
                
                if not request.topic:
                    return {"success": False, "error": "Topic is required"}
                
                coverage = check_topic_similarity(request.topic)
                return {"success": True, "data": coverage}
            except Exception as e:
                logger.error(f"Error checking topic coverage: {e}")
                return {"success": False, "error": str(e)}

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