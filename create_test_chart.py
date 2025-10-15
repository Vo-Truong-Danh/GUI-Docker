import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Create figure
plt.figure(figsize=(10, 6))

# Plot data
plt.plot([1, 2, 3, 4, 5], [2, 4, 6, 8, 10], 'b-', linewidth=2, label='Linear')
plt.plot([1, 2, 3, 4, 5], [1, 4, 9, 16, 25], 'r--', linewidth=2, label='Quadratic')

# Labels and title
plt.title('📊 Test Chart - Demo', fontsize=16, fontweight='bold')
plt.xlabel('X axis', fontsize=12)
plt.ylabel('Y axis', fontsize=12)
plt.legend(fontsize=10)
plt.grid(True, alpha=0.3)

# Save
plt.savefig('/tmp/demo_chart.png', dpi=100, bbox_inches='tight')
print('✅ Chart saved to /tmp/demo_chart.png')
