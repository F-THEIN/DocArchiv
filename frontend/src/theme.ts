import { createTheme, rem } from '@mantine/core';

export const theme = createTheme({
  primaryColor: 'yellow',
  primaryShade: 5,
  fontFamily: '"Open Sans", sans-serif',
  headings: {
    fontFamily: '"Montserrat", sans-serif',
    fontWeight: '800',
  },
  defaultGradient: {
    from: 'yellow.5',
    to: 'yellow.7',
    deg: 90,
  },
  radius: {
    xs: rem(4),
    sm: rem(6),
    md: rem(10),
    lg: rem(14),
    xl: rem(18),
  },
  defaultRadius: 'md',
});
