import java.util.*;

class Edge {
    int x, y;
    Edge(int x, int y) {
        this.x = x;
        this.y = y;
    }
}

public class Dijikistra {
    static void digialgo(List<List<Edge>> outer, int start, int totalNodes) {
        int[] dist = new int[totalNodes];
        Arrays.fill(dist, Integer.MAX_VALUE);
        dist[start] = 0;

        PriorityQueue<int[]> q;
        q = new PriorityQueue<>(Comparator.comparingInt(a -> a[1]));
        q.add(new int[]{start, 0});

        while (!q.isEmpty()) {
            int[] curr = q.poll();
            int a = curr[0], b = curr[1];

            for (Edge e : outer.get(a)) {
                int vertex = e.x, weight = e.y;
                if (dist[vertex] > b + weight) {
                    dist[vertex] = b + weight;
                    q.add(new int[]{vertex, dist[vertex]});
                }
            }
        }

        for (int i = 0; i < totalNodes; i++) {
            System.out.println(dist[i]);
        }
    }

    public static void main(String[] args) {
        Scanner in = new Scanner(System.in);
        int v = in.nextInt();
        int e = in.nextInt();
        List<List<Edge>> outer = new ArrayList<>();

        for (int i = 0; i < v; i++) {
            outer.add(new ArrayList<>());
        }

        for (int i = 0; i < e; i++) {
            int x = in.nextInt();
            int z = in.nextInt();
            int w = in.nextInt();
            outer.get(x).add(new Edge(z, w));
            outer.get(z).add(new Edge(x, w));
        }

        int source = in.nextInt();
        digialgo(outer, source, v);
    }
}
