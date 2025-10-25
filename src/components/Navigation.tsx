"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

export default function Navigation() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const closeMenu = () => setIsMenuOpen(false);

  return (
    <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
      isScrolled
        ? 'bg-white/95 backdrop-blur-md shadow-lg border-b border-gray-200/50'
        : 'bg-white/90 backdrop-blur-sm border-b border-gray-100'
    }`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center">
            <Link href="/" className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">BC</span>
              </div>
              <span className="text-xl font-bold text-gray-900">BanglaChat Pro</span>
            </Link>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-6">
            <Link
              href="#features"
              className="text-gray-700 hover:text-blue-600 transition-colors font-medium text-sm"
            >
              Features
            </Link>
            <Link
              href="#pricing"
              className="text-gray-700 hover:text-blue-600 transition-colors font-medium text-sm"
            >
              Pricing
            </Link>
            <Link
              href="#integrations"
              className="text-gray-700 hover:text-blue-600 transition-colors font-medium text-sm"
            >
              Integrations
            </Link>
            <Link
              href="/login"
              className="text-gray-700 hover:text-blue-600 transition-colors font-medium text-sm"
            >
              Sign In
            </Link>
            <Link
              href="/register"
              className="bg-gradient-to-r from-blue-500 to-purple-500 text-white px-6 py-2.5 rounded-lg hover:from-blue-600 hover:to-purple-600 transition-all duration-300 font-medium text-sm shadow-lg hover:shadow-xl transform hover:scale-105"
            >
              Start Free Trial
            </Link>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="p-2 rounded-lg text-gray-700 hover:text-blue-600 hover:bg-blue-50 transition-colors"
              aria-label="Toggle menu"
            >
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                {isMenuOpen ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        <div className={`md:hidden transition-all duration-300 overflow-hidden ${
          isMenuOpen ? 'max-h-96 opacity-100' : 'max-h-0 opacity-0'
        }`}>
          <div className="border-t border-gray-200 py-4 space-y-4">
            <Link
              href="#features"
              className="block text-gray-700 hover:text-blue-600 transition-colors font-medium"
              onClick={closeMenu}
            >
              Features
            </Link>
            <Link
              href="#pricing"
              className="block text-gray-700 hover:text-blue-600 transition-colors font-medium"
              onClick={closeMenu}
            >
              Pricing
            </Link>
            <Link
              href="#integrations"
              className="block text-gray-700 hover:text-blue-600 transition-colors font-medium"
              onClick={closeMenu}
            >
              Integrations
            </Link>
            <div className="pt-4 border-t border-gray-200 space-y-3">
              <Link
                href="/login"
                className="block w-full text-center text-gray-700 hover:text-blue-600 transition-colors font-medium py-2"
                onClick={closeMenu}
              >
                Sign In
              </Link>
              <Link
                href="/register"
                className="block w-full bg-gradient-to-r from-blue-500 to-purple-500 text-white py-3 px-4 rounded-lg hover:from-blue-600 hover:to-purple-600 transition-all duration-300 font-medium text-center shadow-lg"
                onClick={closeMenu}
              >
                Start Free Trial
              </Link>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}
