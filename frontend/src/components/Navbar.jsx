import React from 'react';

export default function Navbar({ user, onLogout, onShowRegister }) {
  return (
    <header className="bg-white shadow">
      <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
        <div className="text-xl font-semibold">Маркетплейс</div>
        <nav className="flex items-center gap-4">
          {user ? (
            <>
              <span className="text-gray-700">Привет, пользователь #{user}</span>
              <button className="text-sm text-red-600" onClick={onLogout}>Выйти</button>
            </>
          ) : (
            <>
              <button className="text-sm text-blue-700" onClick={() => onShowRegister(false)}>Войти</button>
              <button className="text-sm text-blue-700" onClick={() => onShowRegister(true)}>Регистрация</button>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
