import { fireEvent, render, screen } from '@testing-library/react';
import { ThemeProvider, useTheme } from './ThemeContext';

function Probe() {
  const { isDark, toggleTheme } = useTheme();
  return (
    <button type="button" onClick={toggleTheme}>
      {isDark ? 'dark' : 'light'}
    </button>
  );
}

describe('ThemeContext', () => {
  beforeEach(() => {
    localStorage.clear();
    document.documentElement.classList.remove('dark');
  });

  it('defaults to dark mode when no saved preference exists', () => {
    render(
      <ThemeProvider>
        <Probe />
      </ThemeProvider>,
    );

    expect(screen.getByRole('button')).toHaveTextContent('dark');
    expect(localStorage.getItem('crm-theme')).toBe('dark');
    expect(document.documentElement.classList.contains('dark')).toBe(true);
  });

  it('reads stored theme and toggles correctly', () => {
    localStorage.setItem('crm-theme', 'light');

    render(
      <ThemeProvider>
        <Probe />
      </ThemeProvider>,
    );

    const button = screen.getByRole('button');
    expect(button).toHaveTextContent('light');
    expect(document.documentElement.classList.contains('dark')).toBe(false);

    fireEvent.click(button);
    expect(button).toHaveTextContent('dark');
    expect(localStorage.getItem('crm-theme')).toBe('dark');
    expect(document.documentElement.classList.contains('dark')).toBe(true);
  });
});
