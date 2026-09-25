import React from 'react';
import styled, { css } from 'styled-components';

const Button = styled.button<{ 
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'small' | 'medium' | 'large';
  disabled?: boolean;
}>`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: ${({ size }) => size === 'small' ? '8px 16px' : size === 'large' ? '12px 24px' : '10px 20px'};
  font-weight: 600;
  border-radius: 6px;
  border: none;
  cursor: ${({ disabled }) => disabled ? 'not-allowed' : 'pointer'};
  font-size: 14px;
  transition: all 0.2s ease;
  ${({ variant, disabled }) => {
    if (disabled) return css`background-color: #cccccc; color: #666666; cursor: not-allowed;`;
    switch (variant) {
      case 'primary': return css`background-color: #0070f3; color: white;`;
      case 'danger': return css`background-color: #d32f2f; color: white;`;
      case 'secondary':
      default: return css`background-color: #f0f0f0; color: #333333; border: 1px solid #ddd;`;
    }
  }}
  &:hover:not(:disabled) {
    ${({ variant }) => {
      switch (variant) {
        case 'primary': return css`background-color: #0051cc;`;
        case 'danger': return css`background-color: #b71c1c;`;
        case 'secondary':
        default: return css`background-color: #e0e0e0;`;
      }
    }}
  }
  &:active:not(:disabled) { transform: scale(0.98); }
`;

const Input = styled.input<{ size?: 'small' | 'medium' | 'large'; error?: boolean; }>`
  padding: ${({ size }) => size === 'small' ? '8px 12px' : size === 'large' ? '12px 16px' : '10px 14px'};
  border: 1px solid ${({ error }) => error ? '#ff6b6b' : '#ddd'};
  border-radius: 6px; font-size: 14px; width: 100%; box-sizing: border-box;
  transition: all 0.2s ease;
  &:focus { outline: none; border-color: ${({ error }) => error ? '#ff6b6b' : '#0070f3'}; box-shadow: 0 0 0 2px rgba(0, 112, 243, 0.2); }
  &::placeholder { color: #aaa; }
`;

const TextArea = styled.textarea<{ size?: 'small' | 'medium' | 'large'; error?: boolean; }>`
  padding: ${({ size }) => size === 'small' ? '8px 12px' : size === 'large' ? '12px 16px' : '10px 14px'};
  border: 1px solid ${({ error }) => error ? '#ff6b6b' : '#ddd'}; border-radius: 6px;
  font-size: 14px; width: 100%; min-height: 80px; resize: vertical; box-sizing: border-box;
  transition: all 0.2s ease;
  &:focus { outline: none; border-color: ${({ error }) => error ? '#ff6b6b' : '#0070f3'}; box-shadow: 0 0 0 2px rgba(0, 112, 243, 0.2); }
  &::placeholder { color: #aaa; }
`;

const Select = styled.select<{ size?: 'small' | 'medium' | 'large'; error?: boolean; }>`
  padding: ${({ size }) => size === 'small' ? '8px 12px' : size === 'large' ? '12px 16px' : '10px 14px'};
  border: 1px solid ${({ error }) => error ? '#ff6b6b' : '#ddd'}; border-radius: 6px;
  font-size: 14px; width: 100%; background-color: white; appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3E%3Cpath d='M6 4l2.5 2.5-2.5 2.5' fill='%23666'/%3E%3C/svg%3E");
  background-repeat: no-repeat; background-position: right 12px center; cursor: pointer;
  &:focus { outline: none; border-color: ${({ error }) => error ? '#ff6b6b' : '#0070f3'}; box-shadow: 0 0 0 2px rgba(0, 112, 243, 0.2); }
  &::-ms-expand { display: none; }
`;

const Card = styled.div<{ elevated?: boolean; bordered?: boolean; }>`
  background-color: white; border-radius: 8px;
  border: ${({ bordered }) => bordered ? '1px solid #eee' : 'none'};
  box-shadow: ${({ elevated }) => elevated ? '0 2px 8px rgba(0,0,0,0.1)' : 'none'};
  padding: ${({ elevated }) => elevated ? '24px' : '16px'}; margin-bottom: 16px;
`;

const Badge = styled.span<{ variant?: 'success' | 'warning' | 'info' | 'error'; size?: 'small' | 'medium' | 'large'; }>`
  display: inline-flex; align-items: center;
  padding: ${({ size }) => size === 'small' ? '2px 8px' : size === 'large' ? '6px 12px' : '4px 10px'};
  border-radius: 12px; font-size: ${({ size }) => size === 'small' ? '10px' : size === 'large' ? '14px' : '12px'};
  font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;
  ${({ variant }) => {
    switch (variant) {
      case 'success': return css`background-color: #d4edda; color: #155724;`;
      case 'warning': return css`background-color: #fff3cd; color: #856404;`;
      case 'error': return css`background-color: #f8d7da; color: #721c24;`;
      case 'info':
      default: return css`background-color: #d1ecf1; color: #0c5460;`;
    }
  }}
`;

const Avatar = styled.img<{ size?: number; rounded?: boolean; }>`
  width: ${({ size }) => size || 40}px; height: ${({ size }) => size || 40}px;
  border-radius: ${({ rounded }) => rounded ? '50%' : '4px'}; object-fit: cover;
  border: 2px solid ${({ rounded }) => rounded ? '#fff' : 'none'};
  box-shadow: ${({ rounded }) => rounded ? '0 2px 4px rgba(0,0,0,0.1)' : 'none'};
`