import React, { useEffect, useState } from 'react';

export default function ProductDetails({ id, onClose, userId }) {
  const [product, setProduct] = useState(null);
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetch(`http://localhost:8000/products/${id}`)
      .then(res => res.json())
      .then(setProduct)
      .catch(() => setMessage('Ошибка загрузки'));
  }, [id]);

  const handlePurchase = async () => {
    if (!userId) return setMessage('Войдите, чтобы купить');
    const res = await fetch(`http://localhost:8000/purchase?product_id=${id}&buyer_id=${userId}`, { method: 'POST' });
    if (res.ok) {
      setMessage('Покупка успешна');
    } else {
      setMessage('Ошибка покупки');
    }
  };

  if (!product) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black opacity-50" onClick={onClose}></div>
      <div className="relative bg-white rounded-lg shadow-lg max-w-2xl w-full p-6 z-10">
        <button className="text-sm text-gray-500" onClick={onClose}>✕</button>
        <h2 className="text-2xl font-bold mt-2">{product.title}</h2>
        <p className="text-gray-600 mt-2">{product.description}</p>
        <div className="mt-4 flex items-center justify-between">
          <div className="text-xl font-semibold">{product.price} ₽</div>
          <button className="bg-green-600 text-white px-4 py-2 rounded" onClick={handlePurchase}>Купить</button>
        </div>
        {product.file_url && (
          <div className="mt-3 text-sm text-blue-600">
            <a href={product.file_url} target="_blank" rel="noreferrer">Скачать / Просмотреть файл</a>
          </div>
        )}
        {message && <div className="mt-3 text-sm text-gray-600">{message}</div>}
      </div>
    </div>
  );
}
