import React from 'react';

export default function ProductCard({ product, onView }) {
  return (
    <div className="bg-white rounded-lg shadow p-4 flex flex-col">
      <div className="h-40 bg-gray-100 rounded mb-3 flex items-center justify-center text-gray-400">Файл/Превью</div>
      <h3 className="text-lg font-semibold">{product.title}</h3>
      <p className="text-sm text-gray-500 flex-1">{product.description}</p>
      <div className="flex items-center justify-between mt-3">
        <div className="text-lg font-bold">{product.price} ₽</div>
        <div className="flex gap-2">
          <button className="text-sm text-blue-700" onClick={() => onView(product.id)}>Открыть</button>
          <button className="bg-green-600 text-white px-3 py-1 rounded text-sm">Купить</button>
        </div>
      </div>
    </div>
  );
}
