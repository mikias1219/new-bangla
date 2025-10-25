// BanglaChatPro Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Confirm delete actions
    const deleteButtons = document.querySelectorAll('[data-confirm-delete]');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm-delete') || 'Are you sure you want to delete this item?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });
});

// Chat Interface Functions
function sendMessage() {
    const input = document.getElementById('message-input');
    const message = input.value.trim();

    if (!message) return;

    // Add user message to chat
    addMessageToChat('user', message);

    // Clear input
    input.value = '';

    // Send to server
    fetch('/api/chat/send/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({
            content: message,
            conversation_id: getCurrentConversationId()
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.ai_message) {
            setTimeout(() => {
                addMessageToChat('ai', data.ai_message.content);
            }, 500); // Simulate typing delay
        }
    })
    .catch(error => {
        console.error('Error sending message:', error);
        addMessageToChat('system', 'Sorry, there was an error sending your message.');
    });
}

function addMessageToChat(sender, content) {
    const chatMessages = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message-bubble ${sender}`;

    const contentDiv = document.createElement('div');
    contentDiv.textContent = content;
    messageDiv.appendChild(contentDiv);

    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function getCurrentConversationId() {
    // Get conversation ID from URL or form
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('conversation');
}

// Voice Interface Functions
let mediaRecorder;
let audioChunks = [];

function startRecording() {
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];

            mediaRecorder.ondataavailable = event => {
                audioChunks.push(event.data);
            };

            mediaRecorder.onstop = () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                uploadVoiceRecording(audioBlob);
            };

            mediaRecorder.start();
            updateRecordingUI(true);
        })
        .catch(error => {
            console.error('Error accessing microphone:', error);
            alert('Error accessing microphone. Please check permissions.');
        });
}

function stopRecording() {
    if (mediaRecorder && mediaRecorder.state === 'recording') {
        mediaRecorder.stop();
        updateRecordingUI(false);
    }
}

function uploadVoiceRecording(audioBlob) {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.wav');
    formData.append('conversation_id', getCurrentConversationId());

    fetch('/voice/upload/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken()
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.transcription) {
            addMessageToChat('user', data.transcription);
            // Trigger AI response
            sendMessageFromVoice(data.transcription);
        }
    })
    .catch(error => {
        console.error('Error uploading voice recording:', error);
    });
}

function sendMessageFromVoice(transcription) {
    fetch('/api/chat/send/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({
            content: transcription,
            conversation_id: getCurrentConversationId()
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.ai_message) {
            setTimeout(() => {
                addMessageToChat('ai', data.ai_message.content);
                // Optionally synthesize speech for AI response
                synthesizeSpeech(data.ai_message.content);
            }, 500);
        }
    });
}

function synthesizeSpeech(text) {
    fetch('/voice/synthesize/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({ text: text })
    })
    .then(response => response.json())
    .then(data => {
        if (data.audio_url) {
            // Play synthesized speech
            const audio = new Audio(data.audio_url);
            audio.play();
        }
    });
}

function updateRecordingUI(isRecording) {
    const recordButton = document.getElementById('record-button');
    const indicator = document.getElementById('recording-indicator');

    if (isRecording) {
        recordButton.textContent = 'Stop Recording';
        recordButton.classList.remove('btn-primary');
        recordButton.classList.add('btn-danger');
        indicator.classList.remove('d-none');
    } else {
        recordButton.textContent = 'Start Recording';
        recordButton.classList.remove('btn-danger');
        recordButton.classList.add('btn-primary');
        indicator.classList.add('d-none');
    }
}

// Utility Functions
function getCsrfToken() {
    // Get CSRF token from cookie
    const name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Form validation helpers
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validatePassword(password) {
    return password.length >= 8;
}

// Real-time updates (for future implementation)
function initializeRealTimeUpdates() {
    // WebSocket or Server-Sent Events could be implemented here
    // for real-time chat updates, notifications, etc.
}

// Initialize real-time updates on page load
initializeRealTimeUpdates();

// Export functions for global access
window.sendMessage = sendMessage;
window.startRecording = startRecording;
window.stopRecording = stopRecording;
