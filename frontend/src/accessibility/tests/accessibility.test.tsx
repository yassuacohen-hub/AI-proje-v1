import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {
  ButtonComponent,
  InputComponent,
  SelectComponent,
  TextAreaComponent,
  CardComponent,
  BadgeComponent,
  AvatarComponent,
  ModalComponent,
} from '../../components/base_ui';

describe('WCAG 2.1 AA — Bilesen Erisilebilirlik Testleri', () => {
  describe('1.1.1 — Gorsel Olmayan Alternatifler (A)', () => {
    it('Avatar alt niteligi zorunlu ve erisilebilir adi var', () => {
      render(<AvatarComponent src="/a.png" alt="Kullanici avatari" />);
      expect(screen.getByRole('img', { name: 'Kullanici avatari' })).toBeTruthy();
    });
  });

  describe('2.1.1 — Klavye (A)', () => {
    it('Button klavyeyle aktive edilir', async () => {
      const onClick = vi.fn();
      render(<ButtonComponent onClick={onClick}>Kaydet</ButtonComponent>);
      await userEvent.tab();
      expect(document.activeElement).toBeTruthy();
      await userEvent.keyboard('{Enter}');
      expect(onClick).toHaveBeenCalledTimes(1);
    });

    it('Input klavyeyle yazilabilir', async () => {
      render(<InputComponent aria-label="E-posta" />);
      await userEvent.tab();
      await userEvent.keyboard('test@ornek.com');
      expect((screen.getByLabelText('E-posta') as HTMLInputElement).value).toBe('test@ornek.com');
    });
  });

  describe('2.4.7 — Odak Gorunur (AA)', () => {
    it('Modal acildiginda odak kapatma butonuna tasinir', () => {
      render(<ModalComponent isOpen onClose={() => {}} title="Test">icerik</ModalComponent>);
      expect(document.activeElement?.getAttribute('aria-label')).toBe('Close modal');
    });
  });

  describe('2.1.2 — Klavye Tuzagi Yok (A)', () => {
    it('Escape tusu modal kapatir', async () => {
      const onClose = vi.fn();
      render(<ModalComponent isOpen onClose={onClose} title="Test">x</ModalComponent>);
      await userEvent.keyboard('{Escape}');
      expect(onClose).toHaveBeenCalledTimes(1);
    });
  });

  describe('4.1.2 — Ad, Rol, Deger (A)', () => {
    it('Modal role=dialog ve aria-modal=true', () => {
      render(<ModalComponent isOpen onClose={() => {}} title="Ayarlar">x</ModalComponent>);
      const dialog = screen.getByRole('dialog');
      expect(dialog.getAttribute('aria-modal')).toBe('true');
      expect(dialog.getAttribute('aria-label')).toBe('Ayarlar');
    });

    it('Kapatma butonunun erisilebilir adi var', () => {
      render(<ModalComponent isOpen onClose={() => {}}>x</ModalComponent>);
      expect(screen.getByRole('button', { name: 'Close modal' })).toBeTruthy();
    });
  });

  describe('3.3.1 — Hata Tanımlama (A)', () => {
    it('Input error prop destekler', () => {
      render(<InputComponent aria-label="Ad" error />);
      expect(screen.getByLabelText('Ad')).toBeTruthy();
    });
  });

  describe('2.4.3 — Odak Sırası (A): pozitif tabindex kullanilmaz', () => {
    it('hicbir bilesende pozitif tabindex yok', () => {
      const { container } = render(
        <div>
          <ButtonComponent>Tamam</ButtonComponent>
          <InputComponent aria-label="x" />
          <CardComponent>Kart</CardComponent>
          <BadgeComponent>Yeni</BadgeComponent>
        </div>,
      );
      const positives = Array.from(container.querySelectorAll('[tabindex]')).filter(
        (el) => Number(el.getAttribute('tabindex')) > 0,
      );
      expect(positives).toHaveLength(0);
    });
  });

  describe('Select ve TextArea native semantik', () => {
    it('Select dogru HTML elementi', () => {
      render(
        <SelectComponent aria-label="Rol">
          <option value="admin">Admin</option>
        </SelectComponent>,
      );
      expect(screen.getByLabelText('Rol').tagName).toBe('SELECT');
    });

    it('TextArea dogru HTML elementi', () => {
      render(<TextAreaComponent aria-label="Not" />);
      expect(screen.getByLabelText('Not').tagName).toBe('TEXTAREA');
    });
  });
});