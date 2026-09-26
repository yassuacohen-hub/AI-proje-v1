import type { Meta, StoryObj } from '@storybook/react';
import {
  ButtonComponent,
  InputComponent,
  TextAreaComponent,
  SelectComponent,
  CardComponent,
  BadgeComponent,
  AvatarComponent,
  ModalComponent,
} from './base_ui';
import { useState } from 'react';

const meta = {
  title: 'Base UI/Bileşenler',
  component: ButtonComponent,
  parameters: { layout: 'centered' },
  tags: ['autodocs'],
  argTypes: {
    variant: { control: 'select', options: ['primary', 'secondary', 'danger'] },
    size: { control: 'select', options: ['small', 'medium', 'large'] },
  },
} satisfies Meta<typeof ButtonComponent>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Primary: Story = { args: { children: 'Primary Button', variant: 'primary' } };
export const Secondary: Story = { args: { children: 'Secondary Button', variant: 'secondary' } };
export const Danger: Story = { args: { children: 'Danger Button', variant: 'danger' } };
export const Disabled: Story = { args: { children: 'Disabled', disabled: true } };
export const Small: Story = { args: { children: 'Small', size: 'small' } };
export const Large: Story = { args: { children: 'Large', size: 'large' } };

export const AllInputs: Story = {
  render: () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', width: '320px' }}>
      <InputComponent aria-label="Ad" placeholder="Ad" />
      <InputComponent aria-label="Hatali" placeholder="Hatali alan" error />
      <TextAreaComponent aria-label="Aciklama" placeholder="Aciklama" />
      <SelectComponent aria-label="Rol">
        <option value="admin">Admin</option>
        <option value="user">User</option>
      </SelectComponent>
    </div>
  ),
};

export const CardExample: Story = {
  render: () => (
    <CardComponent elevated bordered>
      <h4>Kart Basligi</h4>
      <p>Kart icerigi burada yer alir.</p>
    </CardComponent>
  ),
};

export const AllBadges: Story = {
  render: () => (
    <div style={{ display: 'flex', gap: '8px' }}>
      <BadgeComponent variant="success">Basarili</BadgeComponent>
      <BadgeComponent variant="warning">Uyari</BadgeComponent>
      <BadgeComponent variant="error">Hata</BadgeComponent>
      <BadgeComponent variant="info">Bilgi</BadgeComponent>
    </div>
  ),
};

export const AvatarExample: Story = {
  render: () => (
    <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
      <AvatarComponent src="https://i.pravatar.cc/80?img=1" alt="Kullanici 1" size={40} />
      <AvatarComponent src="https://i.pravatar.cc/80?img=2" alt="Kullanici 2" size={64} rounded={false} />
    </div>
  ),
};

export const ModalExample: Story = {
  render: function ModalDemo() {
    const [open, setOpen] = useState(false);
    return (
      <div>
        <ButtonComponent onClick={() => setOpen(true)}>Modal ac</ButtonComponent>
        <ModalComponent isOpen={open} onClose={() => setOpen(false)} title="Ornek Modal">
          <p>Escape tusu ile kapatabilirsiniz.</p>
        </ModalComponent>
      </div>
    );
  },
};