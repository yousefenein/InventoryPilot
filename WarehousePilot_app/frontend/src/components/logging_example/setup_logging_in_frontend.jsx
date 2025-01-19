// HOW TO SETUP LOGGING IN FRONTEND

// 1. IMPORT MODULE
import axios from 'axios';

// 2. ADD METHOD TO PUSH YOUR LOG MESSAGES TO DJANGO
const logging = async (level, message) => {
    try {
        await axios.post('/logging/log/', { level, message });
    } catch (error) {
        console.error("Failed to send log to Django", error);
    }
};

// 3. CALL THE METHOD FROM STEP 2 WHEN YOU NEED TO CREATE A LOG
const user = localStorage.getItem('user');
logging('info', `User ${user} created an order`); // example of a log message