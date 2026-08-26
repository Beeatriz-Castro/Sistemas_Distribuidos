import java.io.*;
import java.net.*;
import java.util.*;
/*
* Servidor para processar as requisições de Ping sobre UDP.
*/
public class PingServer {
    private static final double LOSS_RATE = 0.3;
    private static final int AVERAGE_DELAY = 100;//milliseconds
    private static DatagramSocket socket;
    
    public static void main(String[] args) throws Exception {
    while(true){
    // Obter o argumento da linha de comando.
        if (args.length != 1) {
        System.out.println("Required arguments: port");
        return;
        }
        int port = Integer.parseInt(args[0]);
        // Gerador de números aleatórios p/ simular
        Random random = new Random();
        socket = new DatagramSocket(port);
        byte[] buffer = new byte[1024];
        // Criar um pacote de datagrama para comportar o
        DatagramPacket request = new
        DatagramPacket(buffer, buffer.length);
        // Bloquear até que o hospedeiro receba o pacote UDP.
        socket.receive(request);
        // Imprimir os dados recebidos.
        printData(request);
        // Decidir se responde, ou simula perda de pacotes.
        if (random.nextDouble() < LOSS_RATE) {
        System.out.println("Reply not sent.");
        continue;
        }
        // Simular o atraso da rede.
        Thread.sleep((int) (random.nextDouble()) * 2 *
        AVERAGE_DELAY);
        // Enviar resposta.
        InetAddress clientHost = request.getAddress();
        int clientPort = request.getPort();
        byte[] buf = request.getData();
        DatagramPacket reply = new DatagramPacket(buf,
        buf.length, clientHost, clientPort);
        socket.send(reply);
        System.out.println("Reply sent.");
    }
    }
    /*
    * Imprimir o dado de Ping para o trecho de saída padrão.
    */
    private static void printData(DatagramPacket request)
        throws Exception {
        // Obter referências para a ordem de pacotes de
        bytes.
        byte[] buf = request.getData();
        // Envolver os bytes numa cadeia de entrada vetor de
        // você possa ler os dados como uma cadeia de bytes.
        ByteArrayInputStream bais = new
        ByteArrayInputStream(buf);
        // Envolver a cadeia de saída do vetor bytes num
        // entrada, de modo que você possa ler os dados como
        // caracteres.
        InputStreamReader isr = new InputStreamReader(bais);
        // Envolver o leitor de cadeia de entrada num leitor
        // modo que você possa ler os dados de caracteres
        // linha é uma seqüência de caracteres terminados por
        // de \r e \n.)
        BufferedReader br = new BufferedReader(isr);
        // O dado da mensagem está contido numa única linha,
        // linha.
        String line = br.readLine();
        // Imprimir o endereço do hospedeiro e o dado
        System.out.println("Received from "
        + request.getAddress().getHostAddress() +
        ":"+ new String(line));
        }
        }