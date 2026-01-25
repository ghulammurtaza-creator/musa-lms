/**
 * Browser Console Script for Testing Google Meet Webhooks
 * 
 * USAGE:
 * 1. Open browser console (F12)
 * 2. Copy and paste this entire script
 * 3. Use the helper functions:
 * 
 * sendJoin('meeting-id-123', 'teacher@example.com', 'teacher')
 * sendLeave('meeting-id-123', 'student@example.com', 'student')
 */

const WEBHOOK_URL = 'http://localhost:8000/api/webhook/google-meet';
const WEBHOOK_SECRET = '99cda0a876930791b1b15d8163286cefc32273e47e9f52b95735fcd9363ffe12';

async function sendWebhook(meetingId, eventType, userEmail, role) {
  const payload = {
    meeting_id: meetingId,
    event_type: eventType,
    user_email: userEmail,
    role: role,
    timestamp: new Date().toISOString()
  };

  console.log('Sending webhook:', payload);

  try {
    const response = await fetch(WEBHOOK_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Webhook-Secret': WEBHOOK_SECRET
      },
      body: JSON.stringify(payload)
    });

    const data = await response.json();
    
    if (response.ok) {
      console.log('✅ Webhook successful:', data);
      return data;
    } else {
      console.error('❌ Webhook failed:', data);
      return null;
    }
  } catch (error) {
    console.error('❌ Network error:', error);
    return null;
  }
}

// Helper functions
window.sendJoin = (meetingId, userEmail, role = 'student') => {
  return sendWebhook(meetingId, 'join', userEmail, role);
};

window.sendLeave = (meetingId, userEmail, role = 'student') => {
  return sendWebhook(meetingId, 'exit', userEmail, role);
};

// Convenience function to simulate a complete meeting session
window.simulateSession = async (meetingId, participants) => {
  console.log('🎬 Starting meeting simulation...');
  
  // Everyone joins
  for (const p of participants) {
    await sendWebhook(meetingId, 'join', p.email, p.role);
    await new Promise(resolve => setTimeout(resolve, 1000)); // 1 second delay
  }
  
  console.log('✅ All participants joined');
  console.log('⏳ Simulating 3-minute meeting...');
  
  // Wait 3 seconds to simulate meeting time (adjust as needed)
  await new Promise(resolve => setTimeout(resolve, 3000));
  
  // Everyone leaves
  for (const p of participants) {
    await sendWebhook(meetingId, 'exit', p.email, p.role);
    await new Promise(resolve => setTimeout(resolve, 1000)); // 1 second delay
  }
  
  console.log('✅ Meeting simulation complete!');
};

console.log('✅ Webhook testing functions loaded!');
console.log('\nAvailable functions:');
console.log('- sendJoin(meetingId, email, role)');
console.log('- sendLeave(meetingId, email, role)');
console.log('- simulateSession(meetingId, [{email, role}, ...])');
console.log('\nExample:');
console.log('  sendJoin("abc-defg-hij", "teacher@example.com", "teacher")');
console.log('  sendLeave("abc-defg-hij", "student@example.com", "student")');
console.log('\nFull simulation:');
console.log('  simulateSession("abc-defg-hij", [');
console.log('    {email: "teacher@example.com", role: "teacher"},');
console.log('    {email: "student1@example.com", role: "student"}');
console.log('  ])');
