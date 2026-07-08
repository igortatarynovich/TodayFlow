import SwiftUI

struct MapHeatmapGridView: View {
    let cells: [MapHeatmapCellModel]
    let selectedDateISO: String?
    let onSelect: (String) -> Void

    private let columns = Array(repeating: GridItem(.flexible(), spacing: 5), count: 7)

    var body: some View {
        LazyVGrid(columns: columns, spacing: 5) {
            ForEach(cells) { cell in
                Button {
                    if cell.hasMark { onSelect(cell.dateISO) }
                } label: {
                    RoundedRectangle(cornerRadius: 6, style: .continuous)
                        .fill(cell.isFuture ? cell.color.opacity(0.45) : cell.color)
                        .aspectRatio(1, contentMode: .fit)
                        .overlay {
                            if selectedDateISO == cell.dateISO {
                                RoundedRectangle(cornerRadius: 6, style: .continuous)
                                    .stroke(TodayFlowTheme.ink.opacity(0.65), lineWidth: 2)
                            }
                        }
                }
                .buttonStyle(.plain)
                .disabled(!cell.hasMark)
                .opacity(cell.hasMark ? 1 : 0.55)
                .accessibilityLabel(cell.title)
            }
        }
        .frame(maxWidth: 560)
    }
}

struct MapStorySection: View {
    let eyebrow: String
    let text: String

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(eyebrow)
                .font(.caption.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.secondaryInk)
                .textCase(.uppercase)
            Text(text)
                .font(.body)
                .foregroundStyle(TodayFlowTheme.ink)
                .fixedSize(horizontal: false, vertical: true)
        }
        .padding(16)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.white.opacity(0.92))
        .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: 18, style: .continuous)
                .stroke(TodayFlowTheme.gold.opacity(0.18), lineWidth: 1)
        )
    }
}

struct MapLegendRow: View {
    let items: [(label: String, color: Color)]

    var body: some View {
        FlowLayout(spacing: 10) {
            ForEach(items, id: \.label) { item in
                HStack(spacing: 6) {
                    RoundedRectangle(cornerRadius: 4, style: .continuous)
                        .fill(item.color)
                        .frame(width: 12, height: 12)
                    Text(item.label)
                        .font(.caption)
                        .foregroundStyle(TodayFlowTheme.secondaryInk)
                }
            }
        }
    }
}

/// Simple horizontal flow for legend chips.
private struct FlowLayout: Layout {
    var spacing: CGFloat = 8

    func sizeThatFits(proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) -> CGSize {
        let rows = computeRows(proposal: proposal, subviews: subviews)
        let height = rows.reduce(0) { $0 + $1.maxHeight + spacing } - (rows.isEmpty ? 0 : spacing)
        return CGSize(width: proposal.width ?? 0, height: max(0, height))
    }

    func placeSubviews(in bounds: CGRect, proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) {
        let rows = computeRows(proposal: proposal, subviews: subviews)
        var y = bounds.minY
        for row in rows {
            var x = bounds.minX
            for item in row.items {
                item.subview.place(at: CGPoint(x: x, y: y), proposal: .unspecified)
                x += item.width + spacing
            }
            y += row.maxHeight + spacing
        }
    }

    private struct Row {
        var items: [(subview: LayoutSubviews.Element, width: CGFloat)] = []
        var maxHeight: CGFloat = 0
    }

    private func computeRows(proposal: ProposedViewSize, subviews: Subviews) -> [Row] {
        let maxWidth = proposal.width ?? .infinity
        var rows: [Row] = []
        var current = Row()
        var x: CGFloat = 0
        for subview in subviews {
            let size = subview.sizeThatFits(.unspecified)
            if x + size.width > maxWidth, !current.items.isEmpty {
                rows.append(current)
                current = Row()
                x = 0
            }
            current.items.append((subview, size.width))
            current.maxHeight = max(current.maxHeight, size.height)
            x += size.width + spacing
        }
        if !current.items.isEmpty { rows.append(current) }
        return rows
    }
}
