import java.util.ArrayList;
import java.util.List;
public class UndirectedClass {
    static void addEdge(List<List<Integer>> outer, int i, int j){
        outer.get(i).add(j);
        outer.get(j).add(i);
    }
    static void traverse(List<List<Integer>> outer){
        for(int i =0;i<outer.size();i++){
            System.out.print(i);
            for(int j=0;j<outer.get(i).size();j++){
                System.out.print("->"+outer.get(i).get(j));
            }
            System.out.println(" ");
        }
    }
    static void remove(List<List<Integer>>outer,int u, int v){
        for(int i=0;i<outer.size();i++){
            if(outer.get(u).get(i) == v){
                outer.get(u).remove(i);
                break;
            }
        }
        for(int i=0;i<outer.size();i++){
            if(outer.get(v).get(i) == u){
                outer.get(v).remove(i);
                break;
            }
        }
    }
    public static void main(String[] args) {
        List<List<Integer>> outer =new ArrayList<>();
        int v=5;
        for(int k = 0; k <v; k++){
            List<Integer> inner=new ArrayList<>();
            outer.add(inner);
        }
        addEdge(outer,0,1);
        addEdge(outer,0,4);
        addEdge(outer,1,4);
        addEdge(outer,1,3);
        addEdge(outer,1,2);
        addEdge(outer,2,3);
        addEdge(outer,3,4);
        remove(outer,1,4);
        remove(outer,2,1);
        traverse(outer);
    }
}
