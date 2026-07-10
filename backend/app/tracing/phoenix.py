import logging

logger = logging.getLogger(__name__)

try:
    import phoenix as px
    from app.config import settings

    class PhoenixTracer:
        def __init__(self):
            self.session = None
        
        def start(self):
            """Start Phoenix tracing session."""
            if not settings.phoenix_enabled:
                return
            
            try:
                # Launch Phoenix in embedded mode
                px.launch_app()
                self.session = px.Client()
                print(f"Phoenix tracing started at http://localhost:{settings.phoenix_port}")
            except Exception as e:
                print(f"Failed to start Phoenix tracing: {e}")
        
        def stop(self):
            """Stop Phoenix tracing session."""
            if self.session:
                try:
                    px.close_app()
                except Exception:
                    pass

except ImportError:
    logger.warning("arize-phoenix not installed. PhoenixTracer is a stub.")

    class PhoenixTracer:
        def __init__(self):
            self.session = None
            logger.warning("PhoenixTracer initialized in stub mode - no tracing available")
        
        def start(self):
            """Start Phoenix tracing session."""
            if not settings.phoenix_enabled:
                return
            logger.warning("PhoenixTracer.start() called but arize-phoenix not installed")
            print("Phoenix tracing not available (arize-phoenix not installed)")
        
        def stop(self):
            """Stop Phoenix tracing session."""
            logger.warning("PhoenixTracer.stop() called but arize-phoenix not installed")
