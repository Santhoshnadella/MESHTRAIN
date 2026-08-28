import { StyleSheet, TextInput, Pressable, ScrollView } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useState } from 'react';

import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { BottomTabInset, MaxContentWidth, Spacing } from '@/constants/theme';
import { useTheme } from '@/hooks/use-theme';

export default function InferenceScreen() {
  const [prompt, setPrompt] = useState("");
  const [result, setResult] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const theme = useTheme();

  const handleRunInference = () => {
    if (!prompt.trim()) return;
    setIsLoading(true);
    setResult("Routing request to MeshTrain network...");
    
    // Mock simulation of P2P network delay
    setTimeout(() => {
      setResult("[ZK Verified] Generated output from remote peer (Hash: 8f2b1a)\n\n" + prompt + " is a very interesting topic. AI networks will fundamentally transform how this operates.");
      setIsLoading(false);
    }, 2000);
  };

  return (
    <ThemedView style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        <ThemedView style={styles.header}>
          <ThemedText type="subtitle">Decentralized Inference</ThemedText>
        </ThemedView>

        <ScrollView style={styles.resultArea}>
          <ThemedText style={{ color: theme.textSecondary }}>
            {result || "Enter a prompt below to run on a remote P2P GPU..."}
          </ThemedText>
        </ScrollView>

        <ThemedView type="backgroundElement" style={styles.inputCard}>
          <TextInput
            style={[styles.input, { color: theme.text, borderColor: theme.border }]}
            placeholder="Type your AI prompt..."
            placeholderTextColor={theme.textSecondary}
            value={prompt}
            onChangeText={setPrompt}
            multiline
          />
          <Pressable 
            style={[styles.button, isLoading && styles.buttonDisabled]} 
            onPress={handleRunInference}
            disabled={isLoading}
          >
            <ThemedText style={styles.buttonText}>
              {isLoading ? "Running..." : "Run (0.05 MC)"}
            </ThemedText>
          </Pressable>
        </ThemedView>
      </SafeAreaView>
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    flexDirection: 'row',
    justifyContent: 'center',
  },
  safeArea: {
    flex: 1,
    paddingHorizontal: Spacing.four,
    gap: Spacing.three,
    paddingBottom: BottomTabInset + Spacing.three,
    maxWidth: MaxContentWidth,
  },
  header: {
    paddingVertical: Spacing.four,
    alignItems: 'center',
  },
  resultArea: {
    flex: 1,
    padding: Spacing.four,
  },
  inputCard: {
    padding: Spacing.four,
    borderRadius: Spacing.four,
    gap: Spacing.three,
  },
  input: {
    borderWidth: 1,
    borderRadius: Spacing.two,
    padding: Spacing.three,
    minHeight: 80,
    textAlignVertical: 'top',
  },
  button: {
    backgroundColor: '#007AFF',
    padding: Spacing.three,
    borderRadius: Spacing.two,
    alignItems: 'center',
  },
  buttonDisabled: {
    backgroundColor: '#333333',
  },
  buttonText: {
    color: '#FFFFFF',
    fontWeight: 'bold',
  },
});
