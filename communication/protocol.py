TOPIC_TASK_REQUEST = "task_request"
TOPIC_TASK_EXECUTE = "task_execute"
TOPIC_TASK_COMPLETED = "task_completed"
TOPIC_AGENT_REGISTER = "agent_register"
TOPIC_AGENT_HEARTBEAT = "agent_heartbeat"
TOPIC_AGENT_STATUS_UPDATE = "agent_status"
TOPIC_SYSTEM_LOG = "system_log"
TOPIC_RESOURCE_UPDATE = "resource_update"
TOPIC_SYSTEM_COMMAND = "system_command" 

CMD_PAUSE_WORKER = "pause_worker"
CMD_RESUME_WORKER = "resume_worker"
CMD_SCALE_OUT = "scale_out"
CMD_SCALE_IN = "scale_in"
CMD_SHUTDOWN_WORKER = "shutdown_worker"

def create_message(topic, sender_id, payload=None, recipient_id=None):
    """Factory function to create a standardized message."""
    return {
        "topic": topic,
        "sender_id": sender_id,
        "recipient_id": recipient_id,
        "payload": payload or {},
    }