import React, { useState } from 'react';

export default function Register({ onRegister }) {
  const [form, setForm] = useState({ username: '', email: '', password: '' });
  const [message, setMessage] = useState('');

  const handleChange = e => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async e => {
    e.preventDefault();
    const res = await fetch('http://localhost:8000/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form)
    });
    if (res.ok) {
      setMessage('Регистрация успешна!');
      onRegister && onRegister();
    } else {
      setMessage('Ошибка регистрации');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white p-6 rounded shadow-md w-full max-w-sm mx-auto mt-8">
      <h2 className="text-2xl font-bold mb-4">Регистрация</h2>
      <input name="username" placeholder="Имя пользователя" className="input" value={form.username} onChange={handleChange} required />
      <input name="email" type="email" placeholder="Email" className="input mt-2" value={form.email} onChange={handleChange} required />
      <input name="password" type="password" placeholder="Пароль" className="input mt-2" value={form.password} onChange={handleChange} required />
      <button className="bg-blue-700 text-white w-full py-2 rounded mt-4 hover:bg-blue-800 transition" type="submit">Зарегистрироваться</button>
      {message && <div className="mt-2 text-center text-sm text-gray-600">{message}</div>}
    </form>
  );
}
