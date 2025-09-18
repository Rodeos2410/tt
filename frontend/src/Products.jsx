import React, { useEffect, useState } from 'react';

export default function Products() {
  const [products, setProducts] = useState([]);

  useEffect(() => {
    fetch('http://localhost:8000/products')
      .then(res => res.json())
      .then(setProducts);
  }, []);

  return (
    <div className="max-w-4xl mx-auto mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
      {products.map(product => (
        <div key={product.id} className="bg-white rounded-lg shadow-md p-4 flex flex-col">
          <h3 className="text-xl font-bold mb-2">{product.title}</h3>
          <p className="text-gray-600 flex-1">{product.description}</p>
          <div className="flex justify-between items-center mt-4">
            <span className="text-lg font-semibold">{product.price} ₽</span>
            <button className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700">Купить</button>
          </div>
        </div>
      ))}
    </div>
  );
}
