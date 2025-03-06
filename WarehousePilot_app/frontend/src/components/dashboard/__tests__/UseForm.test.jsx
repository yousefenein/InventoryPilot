import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import UseForm from './UserForm';
import axios from 'axios';
import { MemoryRouter, Route, Routes } from 'react-router-dom';

jest.mock('axios');

describe('UseForm Component', () => {
  beforeEach(() => {
    localStorage.setItem('token', 'test-token');
    localStorage.setItem('user', JSON.stringify({ role: 'admin' }));
  });

  test('Renders form fields correctly in add mode', async () => {
    render(
      <MemoryRouter>
        <UseForm />
      </MemoryRouter>
    );

    expect(screen.getByLabelText(/first name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /add staff/i })).toBeInTheDocument();
  });

  test('Password generation creates valid password', async () => {
    render(
      <MemoryRouter>
        <UseForm />
      </MemoryRouter>
    );

    fireEvent.click(screen.getByText(/generate password/i));
    const password = screen.getByLabelText(/password/i).value;
    
    expect(password.length).toBeGreaterThanOrEqual(8);
    expect(password.length).toBeLessThanOrEqual(16);
    expect(password).toMatch(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()\-_=+[\]{}|;:,.<>?]).+$/);
  });

  test('Form validation blocks future hire dates', async () => {
    render(
      <MemoryRouter>
        <UseForm />
      </MemoryRouter>
    );

    const dateInput = screen.getByLabelText(/date of hire/i);
    fireEvent.change(dateInput, { target: { value: '2030-01-01' } });
    fireEvent.click(screen.getByRole('button', { name: /add staff/i }));

    await waitFor(() => {
      expect(screen.getByText(/cannot be in the future/i)).toBeInTheDocument();
    });
  });
});
