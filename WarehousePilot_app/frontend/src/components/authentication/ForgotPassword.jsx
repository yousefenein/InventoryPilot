import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import './authentication.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

function ForgotPassword() {
  // State variables
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [shake, setShake] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  // Function to handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setMessage('');
    console.log(email) // Debugging

    // Check if email field is empty
    if (!email) {
      setError('Email is required');
      setShake(true);
      setTimeout(() => setShake(false), 500);
      setIsLoading(false);
      return;
    }

    // Pass email to the API to request a password reset link
    try {
      const response = await axios.post(`${API_BASE_URL}/auth/password-reset-request/`, { email });
      setMessage(response.data.message || 'Password reset link sent to your email');
      setIsLoading(false);
    } catch (error) {
      console.error('Password reset failed:', error);
      setError(error.response?.data?.message || 'Failed to send reset link. Please try again.');
      setShake(true);
      setTimeout(() => setShake(false), 500);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col md:flex-row dark:bg-gray-900">

      {/* Form Section */}
      <div className="w-full md:w-1/2 p-8 flex flex-col justify-center mx-auto max-w-2xl">
        <div className="w-full space-y-8">
          <div className="text-center">
            <img
              src="csf-logo-footer-edited.png"
              alt="Company Logo"
              className="h-16 mx-auto mb-8"
            />
            <h1 className="text-3xl font-bold mb-8 dark:text-white">Forgot Password</h1>
            <p className="text-lg text-gray-600 dark:text-gray-300 mb-8">
              Enter your email address and we'll send you a link to reset your password.
            </p>
          </div>

          {/* Form for email input and submit button */}
          <form onSubmit={handleSubmit} className={`space-y-8 ${shake ? 'animate-shake' : ''}`}>
            <div>
              <label className="block text-lg font-medium mb-3 dark:text-gray-300">
                Email Address
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder="Enter your email"
                className="w-full px-4 py-3 border rounded-lg text-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white dark:placeholder-gray-400"
              />
            </div>

            {/* Submit button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-3 px-4 bg-black text-white rounded-lg transition-colors duration-200 text-lg font-medium hover:bg-gray-800 dark:bg-gray-700 dark:hover:bg-gray-600 dark:text-white disabled:opacity-70"
            >
              {isLoading ? 'Sending...' : 'Send Reset Link'}
            </button>

            {/* Success or error message */}
            {message && (
              <p className="text-green-600 dark:text-green-400 text-lg text-center">
                {message}
              </p>
            )}

            {error && (
              <p className="text-red-600 dark:text-red-400 text-lg text-center">
                {error}
              </p>
            )}

            {/* Back to Login link */}
            <div className="text-center">
              <button
                type="button"
                onClick={() => navigate('/')}
                className="text-lg text-gray-500 hover:underline dark:text-gray-400"
              >
                Back to Login
              </button>
            </div>
          </form>
        </div>
      </div>

      {/* Right side - Image (hidden below 1000px) */}
      <div className="hidden md:block w-1/2 bg-gray-100 dark:bg-gray-800 hide-below-1000">
        <img
          src="sign-in-img1.png"
          alt="Worker with laptop"
          className="w-full h-full object-cover"
        />
      </div>
    </div>
  );
}

export default ForgotPassword;