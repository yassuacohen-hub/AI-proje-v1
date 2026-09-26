import React from 'react';
import styled, { css } from 'styled-components';

// ===================== Styled Components =====================
const Button = styled.button<{ variant?: 'primary' | 'secondary' | 'danger'; size?: 'small' | 'medium' | 'large'; disabled?: boolean; }>`
  display: inline-flex; align-items: center; justify-content: center;
  padding: ${({ size }) => size === 'small' ? '8px 16px' : size === 'large' ? '12px 24px' : '10px 20px'};
  font-weight: 600; border-radius: 6px; border: none; cursor: ${({ disabled }) => disabled ? 'not-allowed' : 'pointer'};
  font-size: 14px; transition: all 0.2s ease;
  ${({ variant, disabled }) => {
    if (disabled) return css`background-color: #cccccc; color: #666666; cursor: not-allowed;`;
    switch (variant) {
      case 'primary': return css`background-color: #0070f3; color: white;`;
      case 'danger': return css`background-color: #d32f2f; color: white;`;
      case 'secondary': default: return css`background-color: #f0f0f0; color: #333333; border: 1px solid #ddd;`;
    }
  }}
  &:hover:not(:disabled) { ${({ variant }) => { switch (variant) { case 'primary': return css`background-color: #0051cc;`; case 'danger': return css`background-color: #b71c1c;`; default: return css`background-color: #e0e0e0;`; }}} }
  &:active:not(:disabled) { transform: scale(0.98); }
`;

const Input = styled.input.withConfig({ shouldForwardProp: (prop) => !['size', 'error'].includes(prop) })<{ size?: 'small' | 'medium' | 'large'; error?: boolean; }>`
  padding: ${({ size }) => size === 'small' ? '8px 12px' : size === 'large' ? '12px 16px' : '10px 14px'};
  border: 1px solid ${({ error }) => error ? '#ff6b6b' : '#ddd'}; border-radius: 6px; font-size: 14px;
  width: 100%; box-sizing: border-box; transition: all 0.2s ease;
  &:focus { outline: none; border-color: ${({ error }) => error ? '#ff6b6b' : '#0070f3'}; box-shadow: 0 0 0 2px rgba(0,112,243,0.2); }
`;

const TextArea = styled.textarea.withConfig({ shouldForwardProp: (prop) => !['size', 'error'].includes(prop) })<{ size?: 'small' | 'medium' | 'large'; error?: boolean; }>`
  padding: ${({ size }) => size === 'small' ? '8px 12px' : size === 'large' ? '12px 16px' : '10px 14px'};
  border: 1px solid ${({ error }) => error ? '#ff6b6b' : '#ddd'}; border-radius: 6px; font-size: 14px;
  width: 100%; min-height: 80px; resize: vertical; box-sizing: border-box;
  &:focus { outline: none; border-color: ${({ error }) => error ? '#ff6b6b' : '#0070f3'}; box-shadow: 0 0 0 2px rgba(0,112,243,0.2); }
`;

const Select = styled.select.withConfig({ shouldForwardProp: (prop) => !['size', 'error'].includes(prop) })<{ size?: 'small' | 'medium' | 'large'; error?: boolean; }>`
  padding: ${({ size }) => size === 'small' ? '8px 12px' : size === 'large' ? '12px 16px' : '10px 14px'};
  border: 1px solid ${({ error }) => error ? '#ff6b6b' : '#ddd'}; border-radius: 6px; font-size: 14px;
  width: 100%; background-color: white; appearance: none; cursor: pointer;
  &:focus { outline: none; border-color: ${({ error }) => error ? '#ff6b6b' : '#0070f3'}; box-shadow: 0 0 0 2px rgba(0,112,243,0.2); }
`;

const Card = styled.div.withConfig({ shouldForwardProp: (prop) => !['elevated', 'bordered'].includes(prop) })<{ elevated?: boolean; bordered?: boolean; }>`
  background-color: white; border-radius: 8px;
  border: ${({ bordered }) => bordered ? '1px solid #eee' : 'none'};
  box-shadow: ${({ elevated }) => elevated ? '0 2px 8px rgba(0,0,0,0.1)' : 'none'};
  padding: ${({ elevated }) => elevated ? '24px' : '16px'}; margin-bottom: 16px;
`;

const Badge = styled.span<{ variant?: 'success' | 'warning' | 'info' | 'error'; size?: 'small' | 'medium' | 'large'; }>`
  display: inline-flex; align-items: center; padding: ${({ size }) => size === 'small' ? '2px 8px' : size === 'large' ? '6px 12px' : '4px 10px'};
  border-radius: 12px; font-size: ${({ size }) => size === 'small' ? '10px' : size === 'large' ? '14px' : '12px'};
  font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;
  ${({ variant }) => { switch (variant) { case 'success': return css`background-color: #d4edda; color: #155724;`; case 'warning': return css`background-color: #fff3cd; color: #856404;`; case 'error': return css`background-color: #f8d7da; color: #721c24;`; default: return css`background-color: #d1ecf1; color: #0c5460;`; }}}
`;

const Avatar = styled.img.withConfig({ shouldForwardProp: (prop) => !['size', 'rounded'].includes(prop) })<{ size?: number; rounded?: boolean; }>`
  width: ${({ size }) => size || 40}px; height: ${({ size }) => size || 40}px; border-radius: ${({ rounded }) => rounded ? '50%' : '4px'}; object-fit: cover;
`;
const ModalOverlay = styled.div.attrs({ role: 'presentation' })`position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,.5);display:flex;align-items:center;justify-content:center;z-index:1000`;
const ModalContent = styled.div.attrs({ role: 'dialog', 'aria-modal': true })<{width?:string;maxWidth?:string}>`background:#fff;border-radius:8px;width:${({width})=>width||'90%'};max-width:${({maxWidth})=>maxWidth||'500px'};max-height:90vh;overflow-y:auto;box-shadow:0 4px 20px rgba(0,0,0,.15)`;
const ModalHeader = styled.div`display:flex;justify-content:space-between;align-items:center;padding:20px 24px;border-bottom:1px solid #eee`;
const ModalTitle = styled.h2`margin:0;font-size:20px;font-weight:600;color:#333`;
const ModalCloseButton = styled.button`background:none;border:none;font-size:24px;line-height:1;cursor:pointer;padding:0;color:#999;&:hover{color:#666}`;
const ModalBody = styled.div`padding:24px`;
const ModalFooter = styled.div`display:flex;justify-content:flex-end;gap:12px;padding:20px 24px;border-top:1px solid #eee`;

// ===================== Component Exports =====================
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> { variant?: 'primary'|'secondary'|'danger'; size?: 'small'|'medium'|'large'; }
export const ButtonComponent: React.FC<ButtonProps> = ({children,variant='primary',size='medium',disabled=false,...p}) => (<Button variant={variant} size={size} disabled={disabled} {...p}>{children}</Button>);
interface InputProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'size'> { size?: 'small' | 'medium' | 'large'; error?: boolean; }
export const InputComponent: React.FC<InputProps> = ({size='medium',...p}) => <Input size={size} {...p} />;
interface TextAreaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> { size?: 'small'|'medium'|'large'; }
export const TextAreaComponent: React.FC<TextAreaProps> = ({size='medium',...p}) => <TextArea size={size} {...p} />;
interface SelectProps extends Omit<React.SelectHTMLAttributes<HTMLSelectElement>, 'size'> { size?: 'small'|'medium'|'large'; error?: boolean; }
export const SelectComponent: React.FC<SelectProps> = ({size='medium',...p}) => <Select size={size} {...p} />;
interface CardProps { children:React.ReactNode; elevated?:boolean; bordered?:boolean; className?:string; }
export const CardComponent: React.FC<CardProps> = ({children,elevated=false,bordered=false,className='',...p}) => <Card elevated={elevated} bordered={bordered} className={className} {...p}>{children}</Card>;
interface BadgeProps { children:React.ReactNode; variant?: 'success'|'warning'|'info'|'error'; size?: 'small'|'medium'|'large'; }
export const BadgeComponent: React.FC<BadgeProps> = ({children,variant='info',size='medium',...p}) => <Badge variant={variant} size={size} {...p}>{children}</Badge>;
interface AvatarProps extends React.ImgHTMLAttributes<HTMLImageElement> { size?:number; rounded?:boolean; alt:string; }
export const AvatarComponent: React.FC<AvatarProps> = ({src,size,rounded=true,alt,...p}) => <Avatar src={src} size={size} rounded={rounded} alt={alt} {...p} />;
interface ModalProps { isOpen:boolean; onClose:()=>void; children:React.ReactNode; title?:string; width?:string; maxWidth?:string; }
export const ModalComponent: React.FC<ModalProps> = ({isOpen,onClose,children,title,width,maxWidth}) => {
  const overlayRef = React.useRef<HTMLDivElement>(null);
  const closeRef = React.useRef<HTMLButtonElement>(null);
  const previouslyFocused = React.useRef<HTMLElement | null>(null);

  React.useEffect(() => {
    if(!isOpen) return;
    previouslyFocused.current = document.activeElement as HTMLElement;
    closeRef.current?.focus();

    const onKeyDown = (e: KeyboardEvent) => {
      if(e.key === 'Escape') { e.stopPropagation(); onClose(); return; }
      if(e.key !== 'Tab' || !overlayRef.current) return;
      const focusables = overlayRef.current.querySelectorAll<HTMLElement>(
        'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])',
      );
      if(focusables.length === 0) return;
      const first = focusables[0];
      const last = focusables[focusables.length - 1];
      if(e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if(!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    };

    document.addEventListener('keydown', onKeyDown);
    return () => {
      document.removeEventListener('keydown', onKeyDown);
      previouslyFocused.current?.focus();
    };
  },[isOpen,onClose]);

  if(!isOpen) return null;
  return (
    <ModalOverlay ref={overlayRef} onClick={onClose} role="presentation">
      <ModalContent width={width} maxWidth={maxWidth} onClick={e=>e.stopPropagation()} role="dialog" aria-modal="true" aria-label={title || 'Modal'}>
        <ModalHeader>{title && <ModalTitle>{title}</ModalTitle>}<ModalCloseButton ref={closeRef} type="button" onClick={onClose} aria-label="Close modal">×</ModalCloseButton></ModalHeader>
        <ModalBody>{children}</ModalBody>
      </ModalContent>
    </ModalOverlay>
  );
};
export { ButtonComponent as Button, InputComponent as Input, TextAreaComponent as TextArea, SelectComponent as Select, CardComponent as Card, BadgeComponent as Badge, AvatarComponent as Avatar, ModalComponent as Modal };
export type { ButtonProps, InputProps, TextAreaProps, SelectProps, CardProps, BadgeProps, AvatarProps, ModalProps };