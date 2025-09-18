import React, { useState } from 'react';

export default function AddProduct({ ownerId, onAdd }) {
  const [form, setForm] = useState({ title: '', description: '', price: '' });
  const [message, setMessage] = useState('');

  const handleChange = e => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async e => {
    e.preventDefault();
    const res = await fetch(`http://localhost:8000/products?owner_id=${ownerId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...form, price: parseFloat(form.price) })
    });
    if (res.ok) {
      setMessage('Товар добавлен!');
      setForm({ title: '', description: '', price: '' });
      onAdd && onAdd();
    } else {
      setMessage('Ошибка добавления');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white p-6 rounded shadow-md w-full max-w-sm mx-auto mt-8">
      <h2 className="text-2xl font-bold mb-4">Добавить товар</h2>
      <input name="title" placeholder="Название" className="input" value={form.title} onChange={handleChange} required />
      <input name="description" placeholder="Описание" className="input mt-2" value={form.description} onChange={handleChange} required />
      <input name="price" type="number" step="0.01" placeholder="Цена" className="input mt-2" value={form.price} onChange={handleChange} required />
      <button className="bg-blue-700 text-white w-full py-2 rounded mt-4 hover:bg-blue-800 transition" type="submit">Добавить</button>
      {message && <div className="mt-2 text-center text-sm text-gray-600">{message}</div>}
    </form>
  );
}
