import React, { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';
import './authentication.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

function ResetPassword() {
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState('');
    const [success, setSuccess] = useState(false);
    const [shake, setShake] = useState(false);
    const { uid, token } = useParams();
    const navigate = useNavigate();

    console.log('UID:', uid, 'Token:', token); //debugging

    const handleResetPassword = async (e) => {
        e.preventDefault();

        if (password !== confirmPassword) {
            setError('Passwords do not match');
            setShake(true);
            setTimeout(() => setShake(false), 500);
            return;
        }

        if (password.length < 8) {
            setError('Password must be at least 8 characters');
            setShake(true);
            setTimeout(() => setShake(false), 500);
            return;
        }

        try {
            await axios.post(`${API_BASE_URL}/auth/password-reset/`, {
                uidb64: uid,
                token: token,
                new_password: password
            });
            setSuccess(true);
            setError('');
        } catch (error) {
            console.error('Password reset failed:', error);
            setError(error.response?.data?.message || 'Password reset failed. Please try again.');
            setShake(true);
            setTimeout(() => setShake(false), 500);
        }
    };

    if (success) {
        return (
            <div className="min-h-screen flex flex-col md:flex-row dark:bg-gray-900">
                <div className="w-full md:w-1/2 p-8 flex flex-col justify-center mx-auto max-w-2xl">
                    <div className="w-full space-y-8">
                        <div className="text-center">
                            <img
                                src="/csf-logo-footer-edited.png"
                                alt="Company Logo"
                                className="h-16 mx-auto mb-8"
                            />
                            <h1 className="text-3xl font-bold mb-8 dark:text-white">Password Reset Successful</h1>
                            <p className="text-lg dark:text-gray-300 mb-8">
                                Your password has been successfully updated. You can now login with your new password.
                            </p>
                            <button
                                onClick={() => navigate('/')}
                                className="w-full py-3 px-4 bg-black text-white rounded-lg transition-colors duration-200 text-lg font-medium hover:bg-gray-800 dark:bg-gray-700 dark:hover:bg-gray-600 dark:text-white"
                            >
                                Return to Login
                            </button>
                        </div>
                    </div>
                </div>
                <div className="hidden md:block w-1/2 bg-gray-100 dark:bg-gray-800 hide-below-1000">
                    <img
                        src="/sign-in-img1.png"
                        alt="Worker with laptop"
                        className="w-full h-full object-cover"
                    />
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen flex flex-col md:flex-row dark:bg-gray-900">
            {/* Reset Password Form - Centered on mobile */}
            <div className="w-full md:w-1/2 p-8 flex flex-col justify-center mx-auto max-w-2xl">
                <div className="w-full space-y-8">
                    <div className="text-center">
                        <img
                            src="/csf-logo-footer-edited.png"
                            alt="Company Logo"
                            className="h-16 mx-auto mb-8"
                        />
                        <h1 className="text-3xl font-bold mb-8 dark:text-white">Reset Password</h1>
                        <p className="text-lg dark:text-gray-300 mb-8">
                            Please enter your new password below.
                        </p>
                    </div>

                    <form onSubmit={handleResetPassword} className={`space-y-8 ${shake ? 'animate-shake' : ''}`}>
                        <div>
                            <label className="block text-lg font-medium mb-3 dark:text-gray-300">
                                New Password
                            </label>
                            <input
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                                placeholder="Enter new password"
                                className="w-full px-4 py-3 border rounded-lg text-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white dark:placeholder-gray-400"
                            />
                        </div>

                        <div>
                            <label className="block text-lg font-medium mb-3 dark:text-gray-300">
                                Confirm New Password
                            </label>
                            <input
                                type="password"
                                value={confirmPassword}
                                onChange={(e) => setConfirmPassword(e.target.value)}
                                required
                                placeholder="Confirm new password"
                                className="w-full px-4 py-3 border rounded-lg text-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white dark:placeholder-gray-400"
                            />
                        </div>

                        <button
                            type="submit"
                            className="w-full py-3 px-4 bg-black text-white rounded-lg transition-colors duration-200 text-lg font-medium hover:bg-gray-800 dark:bg-gray-700 dark:hover:bg-gray-600 dark:text-white"
                        >
                            Reset Password
                        </button>

                        {error && (
                            <p className="text-red-600 dark:text-red-400 text-lg text-center">
                                {error}
                            </p>
                        )}
                    </form>
                </div>
            </div>

            {/* Right side - Image (hidden below 1000px) */}
            <div className="hidden md:block w-1/2 bg-gray-100 dark:bg-gray-800 hide-below-1000">
                <img
                    src="/sign-in-img1.png"
                    alt="Worker with laptop"
                    className="w-full h-full object-cover"
                />
            </div>
        </div>
    );
}

export default ResetPassword;