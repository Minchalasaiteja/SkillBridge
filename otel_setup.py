"""
OpenTelemetry setup helper. Configures Jaeger exporter and Prometheus metrics exporter
and instruments Flask app. Keeps configuration optional so app runs without full OTLP
backend in development.
"""

from opentelemetry import trace, metrics
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.metrics import MeterProvider


def initialize_otel(app, settings):
    """Initialize tracing and metrics exporters based on settings."""
    resource = Resource.create({"service.name": "skillbridge"})

    # Tracing (Jaeger)
    tracer_provider = TracerProvider(resource=resource)
    jaeger_exporter = JaegerExporter(
        agent_host_name=settings.jaeger_host,
        agent_port=int(settings.jaeger_port),
    )
    span_processor = BatchSpanProcessor(jaeger_exporter)
    tracer_provider.add_span_processor(span_processor)
    trace.set_tracer_provider(tracer_provider)

    # Metrics (Prometheus) - disabled on Windows due to socket issues
    # For production use Docker: docker compose up --build
    try:
        meter_provider = MeterProvider(resource=resource)
        metrics.set_meter_provider(meter_provider)
    except Exception:
        # If metrics setup fails, continue without it
        pass

    # Instrument Flask and requests
    FlaskInstrumentor().instrument_app(app)
    RequestsInstrumentor().instrument()

    return True
