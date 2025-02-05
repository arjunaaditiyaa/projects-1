import java.util.Arrays;
import java.util.Scanner;
public class bellmanFord {
    public static void main(String[] args) {
        Scanner in = new Scanner(System.in);
        int v = in.nextInt();
        int e = in.nextInt();
        int[][] edges = new int[e][3];

        for (int i = 0; i < e; i++) {
            edges[i][0] = in.nextInt();
            edges[i][1] = in.nextInt();
            edges[i][2] = in.nextInt();
        }
        int source = in.nextInt();
        bellmanAlgo(v, edges, source);
        in.close();
    }
    static void bellmanAlgo(int v, int[][] edges, int source) {
        int[] distance = new int[v];
        Arrays.fill(distance, (int) 1e8);
        distance[source] = 0;
        for (int i = 0; i < v - 1; i++) {
            for (int[] path : edges) {
                int st = path[0];
                int en = path[1];
                int we = path[2];
                if (distance[st] != (int) 1e8 && distance[st] + we < distance[en]) {
                    distance[en] = distance[st] + we;
                }
            }
        }
        for (int[] path : edges) {
            int st = path[0];
            int en = path[1];
            int we = path[2];
            if (distance[st] != (int) 1e8 && distance[st] + we < distance[en]) {
                System.out.println("Negative weight cycle detected");
                return;
            }
        }
        for (int i = 0; i < v; i++) {
            System.out.println("Vertex " + i + " -> Distance: " + (distance[i] == (int) 1e8 ? "INF" : distance[i]));
        }
    }
}