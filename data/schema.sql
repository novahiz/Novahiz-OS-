-- NOVAHIZ OS — Self-Monitoring Database Schema
-- Version: 7.0
-- Created: 2026-05-27

-- Enable WAL mode for better concurrency
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;

-- ============================================================================
-- ERRORS DETECTED
-- ============================================================================
CREATE TABLE IF NOT EXISTS errors (
    id TEXT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    source TEXT NOT NULL,           -- mcp, daemon, agent, router, cli
    severity TEXT NOT NULL,         -- critical, high, medium, low
    category TEXT NOT NULL,         -- execution, routing, memory, performance, config, network
    message TEXT NOT NULL,
    context JSON,                   -- Additional context data
    stack_trace TEXT,               -- Stack trace if available
    resolved BOOLEAN DEFAULT FALSE,
    resolution TEXT,                -- How it was resolved
    resolved_at DATETIME,
    resolved_by TEXT,               -- auto, user, agent_id
    auto_corrected BOOLEAN DEFAULT FALSE,
    correction_id TEXT,             -- Reference to auto_corrections table
    occurrences INTEGER DEFAULT 1,  -- Number of times this error occurred
    last_occurrence DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_errors_timestamp ON errors(timestamp);
CREATE INDEX IF NOT EXISTS idx_errors_severity ON errors(severity);
CREATE INDEX IF NOT EXISTS idx_errors_source ON errors(source);
CREATE INDEX IF NOT EXISTS idx_errors_category ON errors(category);
CREATE INDEX IF NOT EXISTS idx_errors_resolved ON errors(resolved);

-- ============================================================================
-- AGENT METRICS
-- ============================================================================
CREATE TABLE IF NOT EXISTS agent_metrics (
    id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    tasks_completed INTEGER DEFAULT 0,
    tasks_failed INTEGER DEFAULT 0,
    tasks_timeout INTEGER DEFAULT 0,
    avg_duration_seconds REAL DEFAULT 0,
    min_duration_seconds REAL DEFAULT 0,
    max_duration_seconds REAL DEFAULT 0,
    avg_confidence REAL DEFAULT 0,
    success_rate REAL DEFAULT 0,
    routing_count INTEGER DEFAULT 0,
    routing_success INTEGER DEFAULT 0,
    keywords_triggered JSON,        -- Which keywords triggered this agent
    patterns_detected JSON,         -- Behavioral patterns detected
    improvement_suggestions JSON,   -- Auto-generated suggestions
    model_used TEXT,                -- Primary model used
    error_rate REAL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_agent_metrics_agent ON agent_metrics(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_metrics_timestamp ON agent_metrics(timestamp);

-- ============================================================================
-- AUTO-CORRECTIONS
-- ============================================================================
CREATE TABLE IF NOT EXISTS auto_corrections (
    id TEXT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    target_type TEXT NOT NULL,      -- agent, config, routing_rule, skill, daemon
    target_id TEXT,                 -- Specific target identifier
    issue_detected TEXT NOT NULL,   -- Description of the issue
    issue_id TEXT,                  -- Reference to errors table
    correction_applied TEXT NOT NULL,
    before_state JSON NOT NULL,     -- State before correction
    after_state JSON NOT NULL,      -- State after correction
    success BOOLEAN DEFAULT FALSE,
    validation_result TEXT,         -- Result of post-correction validation
    rollback_available BOOLEAN DEFAULT TRUE,
    rollback_applied BOOLEAN DEFAULT FALSE,
    applied_by TEXT DEFAULT 'auto', -- auto, user
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_auto_corrections_target ON auto_corrections(target_type, target_id);
CREATE INDEX IF NOT EXISTS idx_auto_corrections_timestamp ON auto_corrections(timestamp);
CREATE INDEX IF NOT EXISTS idx_auto_corrections_success ON auto_corrections(success);

-- ============================================================================
-- AGENT LEARNING
-- ============================================================================
CREATE TABLE IF NOT EXISTS agent_learning (
    id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    lesson_type TEXT NOT NULL,      -- pattern, optimization, fix, keyword, model
    lesson_data JSON NOT NULL,      -- The actual learning data
    source_task_id TEXT,            -- Task that triggered this learning
    applied BOOLEAN DEFAULT FALSE,  -- Whether learning was applied
    applied_at DATETIME,
    impact_score REAL DEFAULT 0,    -- Measured impact of this learning
    confidence REAL DEFAULT 0,      -- Confidence in this learning
    validated_by TEXT,              -- Who/what validated this learning
    expires_at DATETIME,            -- When this learning expires (if applicable)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_agent_learning_agent ON agent_learning(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_learning_type ON agent_learning(lesson_type);
CREATE INDEX IF NOT EXISTS idx_agent_learning_applied ON agent_learning(applied);

-- ============================================================================
-- SYSTEM STATE
-- ============================================================================
CREATE TABLE IF NOT EXISTS system_state (
    key TEXT PRIMARY KEY,
    value JSON NOT NULL,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1,
    updated_by TEXT DEFAULT 'system'
);

-- Initial system state
INSERT OR IGNORE INTO system_state (key, value, last_updated) VALUES
    ('monitoring_enabled', '{"enabled": false, "started_at": null}', CURRENT_TIMESTAMP),
    ('autocorrect_enabled', '{"enabled": false, "threshold": 0.8}', CURRENT_TIMESTAMP),
    ('learning_enabled', '{"enabled": true, "auto_apply": false}', CURRENT_TIMESTAMP),
    ('last_health_check', '{"status": "unknown", "timestamp": null}', CURRENT_TIMESTAMP),
    ('system_version', '{"version": "7.0.0", "schema_version": 1}', CURRENT_TIMESTAMP);

-- ============================================================================
-- PERFORMANCE METRICS
-- ============================================================================
CREATE TABLE IF NOT EXISTS performance_metrics (
    id TEXT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    metric_type TEXT NOT NULL,      -- cpu, memory, latency, throughput, error_rate
    metric_name TEXT NOT NULL,
    value REAL NOT NULL,
    unit TEXT,                      -- ms, %, bytes, requests/s
    source TEXT,                    -- daemon, mcp, agent, router
    threshold_warning REAL,
    threshold_critical REAL,
    alert_triggered BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_performance_metrics_type ON performance_metrics(metric_type);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_timestamp ON performance_metrics(timestamp);

-- ============================================================================
-- ROUTING HISTORY
-- ============================================================================
CREATE TABLE IF NOT EXISTS routing_history (
    id TEXT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    task_hash TEXT,                 -- Hash of task for deduplication
    task_preview TEXT,              -- First 100 chars of task
    primary_agent TEXT NOT NULL,
    primary_confidence REAL,
    alternative_agents JSON,        -- Other agents considered
    complexity TEXT,                -- SIMPLE, MEDIUM, COMPLEX
    routing_duration_ms REAL,
    keywords_matched JSON,
    success BOOLEAN,
    feedback_score REAL,            -- User/system feedback
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_routing_history_timestamp ON routing_history(timestamp);
CREATE INDEX IF NOT EXISTS idx_routing_history_agent ON routing_history(primary_agent);

-- ============================================================================
-- ALERTS
-- ============================================================================
CREATE TABLE IF NOT EXISTS alerts (
    id TEXT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    alert_type TEXT NOT NULL,       -- error, performance, security, config
    severity TEXT NOT NULL,         -- critical, high, medium, low
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    context JSON,
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_at DATETIME,
    acknowledged_by TEXT,
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at DATETIME,
    notification_sent BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alerts(timestamp);
CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity);
CREATE INDEX IF NOT EXISTS idx_alerts_acknowledged ON alerts(acknowledged);

-- ============================================================================
-- CONFIGURATION HISTORY (Audit Trail)
-- ============================================================================
CREATE TABLE IF NOT EXISTS config_history (
    id TEXT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    config_type TEXT NOT NULL,      -- agent, routing, system, mcp
    config_key TEXT NOT NULL,
    old_value JSON,
    new_value JSON,
    changed_by TEXT DEFAULT 'system',
    change_reason TEXT,
    rollback_available BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_config_history_timestamp ON config_history(timestamp);
CREATE INDEX IF NOT EXISTS idx_config_history_type ON config_history(config_type);

-- ============================================================================
-- VIEWS FOR QUICK ACCESS
-- ============================================================================

-- Unresolved errors by severity
CREATE VIEW IF NOT EXISTS view_unresolved_errors AS
SELECT
    severity,
    category,
    source,
    COUNT(*) as count,
    MAX(timestamp) as last_occurrence
FROM errors
WHERE resolved = FALSE
GROUP BY severity, category, source
ORDER BY
    CASE severity
        WHEN 'critical' THEN 1
        WHEN 'high' THEN 2
        WHEN 'medium' THEN 3
        WHEN 'low' THEN 4
    END;

-- Agent performance summary
CREATE VIEW IF NOT EXISTS view_agent_summary AS
SELECT
    agent_id,
    COUNT(*) as metric_snapshots,
    AVG(success_rate) as avg_success_rate,
    AVG(avg_duration_seconds) as avg_duration,
    MAX(timestamp) as last_update
FROM agent_metrics
GROUP BY agent_id;

-- Recent auto-corrections
CREATE VIEW IF NOT EXISTS view_recent_corrections AS
SELECT
    target_type,
    target_id,
    correction_applied,
    success,
    timestamp
FROM auto_corrections
ORDER BY timestamp DESC
LIMIT 100;

-- Active alerts
CREATE VIEW IF NOT EXISTS view_active_alerts AS
SELECT
    id,
    alert_type,
    severity,
    title,
    message,
    timestamp
FROM alerts
WHERE resolved = FALSE
ORDER BY
    CASE severity
        WHEN 'critical' THEN 1
        WHEN 'high' THEN 2
        WHEN 'medium' THEN 3
        WHEN 'low' THEN 4
    END,
    timestamp DESC;

-- ============================================================================
-- CLEANUP TRIGGER (Auto-archive old data)
-- ============================================================================
-- Note: Actual cleanup should be done by a maintenance script
-- This is just a placeholder for the strategy

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
