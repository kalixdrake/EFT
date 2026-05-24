import { useMemo } from 'react';
import { StyleSheet, useWindowDimensions } from 'react-native';
import RenderHtml from 'react-native-render-html';
import { marked } from 'marked';
import { colors, spacing } from '../utils/theme';

marked.use({
  gfm: true,
  breaks: true,
});

const tagsStyles = {
  body: {
    color: colors.textSecondary,
    fontSize: 15,
    lineHeight: 22,
  },
  p: {
    marginTop: 0,
    marginBottom: spacing.sm,
  },
  strong: {
    fontWeight: '700',
    color: colors.text,
  },
  em: {
    fontStyle: 'italic',
  },
  h1: {
    fontSize: 22,
    fontWeight: '800',
    color: colors.text,
    marginBottom: spacing.sm,
  },
  h2: {
    fontSize: 18,
    fontWeight: '700',
    color: colors.text,
    marginBottom: spacing.sm,
  },
  h3: {
    fontSize: 16,
    fontWeight: '700',
    color: colors.text,
    marginBottom: spacing.xs,
  },
  ul: {
    marginBottom: spacing.sm,
  },
  ol: {
    marginBottom: spacing.sm,
  },
  li: {
    marginBottom: spacing.xs,
  },
  a: {
    color: colors.primary,
    textDecorationLine: 'underline',
  },
  code: {
    fontFamily: 'monospace',
    backgroundColor: colors.background,
    paddingHorizontal: 4,
    borderRadius: 4,
  },
  pre: {
    backgroundColor: colors.background,
    padding: spacing.sm,
    borderRadius: 8,
    marginBottom: spacing.sm,
  },
  blockquote: {
    borderLeftWidth: 3,
    borderLeftColor: colors.border,
    paddingLeft: spacing.sm,
    marginBottom: spacing.sm,
    color: colors.textSecondary,
  },
  table: {
    borderWidth: 1,
    borderColor: colors.border,
    marginBottom: spacing.sm,
  },
  th: {
    backgroundColor: colors.background,
    padding: spacing.xs,
    fontWeight: '700',
    color: colors.text,
    borderWidth: 1,
    borderColor: colors.border,
  },
  td: {
    padding: spacing.xs,
    borderWidth: 1,
    borderColor: colors.border,
  },
};

export default function MarkdownContent({ content, horizontalPadding = spacing.md * 2 }) {
  const { width } = useWindowDimensions();

  const html = useMemo(() => {
    if (!content?.trim()) return '';
    return marked.parse(content);
  }, [content]);

  if (!html) return null;

  return (
    <RenderHtml
      contentWidth={width - horizontalPadding}
      source={{ html }}
      tagsStyles={tagsStyles}
      baseStyle={styles.base}
    />
  );
}

const styles = StyleSheet.create({
  base: {
    color: colors.textSecondary,
    fontSize: 15,
    lineHeight: 22,
  },
});
